"""
Inbound webhooks: Mailchimp / Constant Contact → CRM.
POST-only, CSRF-exempt endpoints. Verify secret via query param (e.g. ?secret=xxx).
"""
import json
import logging
from urllib.parse import parse_qs

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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


def _build_data_from_flat_form(parsed):
    """
    Build data dict from flattened form keys like data[email], data[merges][FNAME].
    parsed is the result of parse_qs (keys are strings, values are lists of one element).
    """
    data = {}
    for key, val_list in parsed.items():
        if not key.startswith('data[') or not val_list:
            continue
        val = val_list[0]
        # key is e.g. "data[email]" or "data[merges][FNAME]"
        path = key[5:-1].split('][')  # 'data[email]' -> ['email']; 'data[merges][FNAME]' -> ['merges', 'FNAME']
        if not path:
            continue
        d = data
        for i, part in enumerate(path[:-1]):
            if part not in d:
                d[part] = {}
            d = d[part]
        d[path[-1]] = val
    return data


@csrf_exempt
def mailchimp_webhook(request):
    """
    Mailchimp audience webhook: subscribe / unsubscribe / profile update.
    POST: process webhook payload. GET: allow URL verification / browser hit (return 200, no action).
    Body is application/x-www-form-urlencoded with 'type' and 'data' (data may be JSON string).
    See: https://mailchimp.com/developer/marketing/guides/sync-audience-data-webhooks/
    """
    if request.method != 'POST':
        return HttpResponse('Mailchimp webhook endpoint; use POST for events.', status=200)

    logger.info('Mailchimp webhook: POST received (body_len=%s)', len(request.body) if request.body else 0)

    if not _verify_mailchimp_secret(request):
        logger.warning('Mailchimp webhook: invalid or missing secret')
        return HttpResponse(status=403)

    # Parse payload. Mailchimp sends application/x-www-form-urlencoded with 'type' and 'data' (data = JSON string).
    # On Vercel/serverless request.POST may be empty; try request.body. Also accept raw JSON body.
    event_type = request.POST.get('type') or ''
    data_raw = request.POST.get('data')
    body_bytes = request.body
    body_str = None
    if body_bytes:
        body_str = body_bytes.decode('utf-8') if isinstance(body_bytes, bytes) else body_bytes

    parsed = None
    if not data_raw and body_str:
        # Fallback 1: form-encoded body (type=subscribe&data={...} or flattened data[email]=...)
        try:
            parsed = parse_qs(body_str, keep_blank_values=True)
            event_type = (parsed.get('type') or [''])[0]
            data_raw = (parsed.get('data') or [''])[0]
            # Mailchimp may send flattened keys (data[email], data[merges][FNAME]) instead of one data=JSON
            if not data_raw and parsed and event_type:
                flat_data = _build_data_from_flat_form(parsed)
                if flat_data.get('email'):
                    data_raw = flat_data  # use dict directly
        except Exception as e:
            logger.warning('Mailchimp webhook: parse_qs failed: %s', e)
    if not data_raw and body_str and body_str.strip().startswith('{'):
        # Fallback 2: raw JSON body {"type": "subscribe", "data": {...}}
        try:
            payload = json.loads(body_str)
            event_type = (payload.get('type') or '').strip()
            data_raw = payload.get('data')
            if data_raw is not None and not isinstance(data_raw, str):
                data_raw = json.dumps(data_raw)
        except Exception as e:
            logger.warning('Mailchimp webhook: JSON body parse failed: %s', e)

    if not data_raw:
        content_type = request.META.get('CONTENT_TYPE', '')[:80]
        logger.warning(
            'Mailchimp webhook: missing data (type=%s, body_len=%s, content_type=%s)',
            event_type, len(body_bytes) if body_bytes else 0, content_type
        )
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
