"""
Sync opted-in Clients, Leads, and Contacts to Mailchimp or Constant Contact.
Uses credentials from the requesting user's profile.
"""
import hashlib
import logging

import requests

logger = logging.getLogger(__name__)


def _record_payload(record):
    """Build a dict with email, first_name, last_name, phone, address, city, state, zip_code."""
    return {
        'email': (record.get('email') or '').strip().lower(),
        'first_name': (record.get('first_name') or '')[:50],
        'last_name': (record.get('last_name') or '')[:50],
        'phone': (record.get('phone') or '')[:20],
        'address': (record.get('address') or '')[:255],
        'city': (record.get('city') or '')[:100],
        'state': (record.get('state') or '')[:50],
        'zip_code': (record.get('zip_code') or '')[:20],
    }


def _mailchimp_subscriber_hash(email):
    """Mailchimp uses MD5 of lowercased email as subscriber hash."""
    return hashlib.md5(email.lower().encode('utf-8')).hexdigest()


def sync_to_mailchimp(profile, records):
    """
    Add or update members in Mailchimp. Uses profile.mailchimp_api_key and profile.mailchimp_audience_id.
    records: list of dicts with email, first_name, last_name, phone, address, city, state, zip_code.
    Returns: (synced_count, errors_list).
    """
    if not profile.has_mailchimp_connected():
        return 0, [{'email': None, 'error': 'Mailchimp not configured for this user.'}]
    api_key = profile.mailchimp_api_key
    audience_id = (profile.mailchimp_audience_id or '').strip()
    if not audience_id:
        return 0, [{'email': None, 'error': 'Mailchimp Audience ID is required.'}]
    # API key format: key-dc (e.g. xxxxx-us21)
    parts = api_key.split('-')
    dc = parts[-1] if len(parts) > 1 else 'us1'
    base_url = f'https://{dc}.api.mailchimp.com/3.0'
    auth = ('anystring', api_key)
    synced = 0
    errors = []
    for r in records:
        payload = _record_payload(r)
        email = payload['email']
        if not email:
            continue
        subscriber_hash = _mailchimp_subscriber_hash(email)
        url = f'{base_url}/lists/{audience_id}/members/{subscriber_hash}'
        body = {
            'email_address': email,
            'status': 'subscribed',
            'merge_fields': {
                'FNAME': payload['first_name'] or '',
                'LNAME': payload['last_name'] or '',
            },
        }
        if payload['phone']:
            body['merge_fields']['PHONE'] = payload['phone']
        try:
            resp = requests.put(url, json=body, auth=auth, timeout=15)
            if resp.status_code in (200, 201):
                synced += 1
            else:
                errors.append({
                    'email': email,
                    'error': resp.text[:200] or f'HTTP {resp.status_code}',
                })
                logger.warning('Mailchimp sync failed for %s: %s', email, resp.text[:200])
        except requests.RequestException as e:
            errors.append({'email': email, 'error': str(e)[:200]})
            logger.exception('Mailchimp request failed for %s', email)
    return synced, errors


def sync_to_constant_contact(profile, records):
    """
    Add or update contacts in Constant Contact using the V3 API sign_up_form endpoint.
    See: https://developer.constantcontact.com/api_guide/v3_technical_overview.html
    and https://v3.developer.constantcontact.com/api_guide/contacts_create_or_update.html

    Uses profile tokens and profile.constant_contact_list_id.
    records: list of dicts with email, first_name, last_name, phone, address, city, state, zip_code.
    Returns: (synced_count, errors_list).
    """
    if not profile.has_constant_contact_connected():
        return 0, [{'email': None, 'error': 'Constant Contact not configured or List ID missing.'}]
    access_token = (profile.constant_contact_access_token or '').strip()
    list_id = (profile.constant_contact_list_id or '').strip()
    if not access_token or not list_id:
        return 0, [{'email': None, 'error': 'Constant Contact access token and List ID are required.'}]
    # V3 API: https://api.cc.email/v3 (JSON only, Bearer token, Accept/Content-Type application/json)
    base_url = 'https://api.cc.email/v3/contacts/sign_up_form'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    synced = 0
    errors = []
    for r in records:
        payload = _record_payload(r)
        email = payload['email']
        if not email:
            continue
        # V3 sign_up_form: email_address, list_memberships (required); first_name, last_name, phone_number, street_address optional
        body = {
            'email_address': email,
            'first_name': (payload['first_name'] or '')[:50],
            'last_name': (payload['last_name'] or '')[:50],
            'list_memberships': [list_id],
            'create_source': 'Account',  # Contact added from CRM/account
        }
        if payload['phone']:
            body['phone_number'] = (payload['phone'] or '')[:50]
        if payload['address'] or payload['city'] or payload['state'] or payload['zip_code']:
            body['street_address'] = {
                'kind': 'home',
                'street': (payload['address'] or '')[:50],
                'city': (payload['city'] or '')[:50],
                'state': (payload['state'] or '')[:50],
                'postal_code': (payload['zip_code'] or '')[:20],
                'country': 'United States',
            }
        try:
            resp = requests.post(base_url, json=body, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                synced += 1
            else:
                errors.append({
                    'email': email,
                    'error': resp.text[:200] or f'HTTP {resp.status_code}',
                })
                logger.warning('Constant Contact sync failed for %s: %s', email, resp.text[:200])
        except requests.RequestException as e:
            errors.append({'email': email, 'error': str(e)[:200]})
            logger.exception('Constant Contact request failed for %s', email)
    return synced, errors


def get_opted_in_records(user, include_clients=True, include_leads=True, include_contacts=True):
    """
    Return a list of record dicts (email, first_name, last_name, phone, address, city, state, zip_code)
    for Client, Lead, and Contact with newsletter_opt_in=True and non-empty email, scoped to the given user.
    """
    from .models import Client, Lead, Contact
    if user is None:
        return []
    records = []
    if include_clients:
        for c in Client.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
            })
    if include_leads:
        for c in Lead.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
            })
    if include_contacts:
        for c in Contact.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
            })
    # Dedupe by email (keep first)
    seen = set()
    unique = []
    for r in records:
        e = (r.get('email') or '').strip().lower()
        if e and e not in seen:
            seen.add(e)
            unique.append(r)
    return unique


def get_opted_in_records_with_type(user, include_clients=True, include_leads=True, include_contacts=True):
    """
    Like get_opted_in_records but each dict includes 'record_type': 'Client' | 'Lead' | 'Contact'.
    Used for the sync preview page so you can review who will be synced.
    """
    from .models import Client, Lead, Contact
    if user is None:
        return []
    records = []
    if include_clients:
        for c in Client.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
                'record_type': 'Client',
            })
    if include_leads:
        for c in Lead.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
                'record_type': 'Lead',
            })
    if include_contacts:
        for c in Contact.objects.filter(user=user, newsletter_opt_in=True).exclude(email='').exclude(email__isnull=True):
            records.append({
                'email': c.email,
                'first_name': c.first_name or '',
                'last_name': c.last_name or '',
                'phone': c.phone or '',
                'address': c.address or '',
                'city': c.city or '',
                'state': c.state or '',
                'zip_code': c.zip_code or '',
                'record_type': 'Contact',
            })
    # Dedupe by email (keep first)
    seen = set()
    unique = []
    for r in records:
        e = (r.get('email') or '').strip().lower()
        if e and e not in seen:
            seen.add(e)
            unique.append(r)
    return unique
