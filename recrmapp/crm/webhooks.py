"""
Inbound webhooks: Mailchimp / Constant Contact → CRM.
POST-only, CSRF-exempt endpoints. Verify secret via query param (e.g. ?secret=xxx).
"""
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def _get_webhook_lead_owner():
    """Return the User to own Leads created from webhooks (first staff user or WEBHOOK_LEAD_OWNER_ID)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    owner_id = getattr(settings, 'WEBHOOK_LEAD_OWNER_ID', None)
    if owner_id:
        user = User.objects.filter(pk=owner_id, is_active=True).first()
        if user:
            return user
    return User.objects.filter(is_staff=True, is_active=True).order_by('pk').first()


def _verify_mailchimp_secret(request):
    """Mailchimp recommends a hard-to-guess secret in the URL. Check query param."""
    secret = getattr(settings, 'MAILCHIMP_WEBHOOK_SECRET', None)
    if not secret:
        return True  # no secret configured: allow (recommend setting in production)
    return request.GET.get('secret') == secret


@csrf_exempt
@require_http_methods(['POST'])
def mailchimp_webhook(request):
    """
    Mailchimp audience webhook: subscribe / unsubscribe / profile update.
    Body is application/x-www-form-urlencoded with 'type' and 'data' (data may be JSON string).
    See: https://mailchimp.com/developer/marketing/guides/sync-audience-data-webhooks/
    """
    if not _verify_mailchimp_secret(request):
        logger.warning('Mailchimp webhook: invalid or missing secret')
        return HttpResponse(status=403)

    # Parse payload: form-encoded; 'data' is often a JSON string
    event_type = request.POST.get('type') or ''
    data_raw = request.POST.get('data')
    if not data_raw:
        logger.warning('Mailchimp webhook: missing data')
        return HttpResponse(status=400)

    try:
        data = json.loads(data_raw) if isinstance(data_raw, str) else data_raw
        if not isinstance(data, dict):
            data = {}
    except (TypeError, ValueError):
        logger.warning('Mailchimp webhook: data is not valid JSON')
        return HttpResponse(status=400)

    email = (data.get('email') or '').strip().lower()
    if not email:
        logger.warning('Mailchimp webhook: no email in data')
        return HttpResponse(status=400)

    merges = data.get('merges') or {}
    first_name = (merges.get('FNAME') or '').strip()[:100]
    last_name = (merges.get('LNAME') or '').strip()[:100]

    from .models import Lead, Client, Contact

    if event_type == 'unsubscribe':
        # Reflect unsubscribe in CRM: set newsletter_opt_in = False on any matching record
        for lead in Lead.objects.filter(email__iexact=email):
            lead.newsletter_opt_in = False
            lead.save(update_fields=['newsletter_opt_in', 'updated_at'])
        for client in Client.objects.filter(email__iexact=email):
            client.newsletter_opt_in = False
            client.save(update_fields=['newsletter_opt_in', 'updated_at'])
        for contact in Contact.objects.filter(email__iexact=email):
            contact.newsletter_opt_in = False
            contact.save(update_fields=['newsletter_opt_in', 'updated_at'])
        logger.info('Mailchimp webhook: unsubscribed %s', email)
        return HttpResponse(status=200)

    if event_type == 'subscribe' or event_type == 'profile update':
        owner = _get_webhook_lead_owner()
        if not owner:
            logger.error('Mailchimp webhook: no webhook lead owner (set WEBHOOK_LEAD_OWNER_ID or add a staff user)')
            return HttpResponse(status=500)

        # Match by email (any owner); create only if none exist
        lead = Lead.objects.filter(email__iexact=email).first()
        if lead:
            lead.first_name = first_name or lead.first_name
            lead.last_name = last_name or lead.last_name
            lead.referral = lead.referral or 'mailchimp'
            lead.newsletter_opt_in = True
            lead.save(update_fields=['first_name', 'last_name', 'referral', 'newsletter_opt_in', 'updated_at'])
            logger.info('Mailchimp webhook: updated Lead %s', email)
        else:
            Lead.objects.create(
                user=owner,
                email=email,
                first_name=first_name or '',
                last_name=last_name or '',
                referral='mailchimp',
                status='new',
                newsletter_opt_in=True,
            )
            logger.info('Mailchimp webhook: created Lead %s', email)
        return HttpResponse(status=200)

    logger.info('Mailchimp webhook: ignored type %s', event_type)
    return HttpResponse(status=200)
