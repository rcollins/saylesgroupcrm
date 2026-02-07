# 2-Way CRM ↔ Mailchimp / Constant Contact Integration

Summary for further review: syncing the CRM with Mailchimp or Constant Contact for newsletters and lead capture.

---

## Goals

- **Inbound:** Website signups (via Mailchimp/Constant Contact) create or update Leads in the CRM; optionally reflect unsubscribes.
- **Outbound:** Push Clients/Leads (and optionally Contacts) from the CRM to Mailchimp/Constant Contact for newsletters.

---

## 1. Inbound: Email Platform → CRM

### Flow
- User signs up on website → added to Mailchimp/Constant Contact list.
- Provider sends webhook (e.g. "subscribe", "profile update") to our URL.
- Django view creates or updates a **Lead** (match by email); optionally update newsletter status on existing Client/Lead.

### Requirements
- **Webhook endpoint(s):** POST-only URL(s), e.g. `/api/webhooks/mailchimp/`, `/api/webhooks/constant-contact/`.
- **Security:** Verify webhook signature/secret (both providers support this). No login; URL + secret treated as credential.
- **CSRF:** Exempt webhook URL from CSRF (external server POST).
- **Mapping:** Provider payload → Lead: `email`, `first_name`, `last_name`, `phone`, address fields; set `referral='website'` (or `mailchimp`/`constant_contact`), `status='new'`.
- **Duplicates:** `get_or_create` by email (or update existing Lead/Client).
- **Unsubscribe (optional):** Handle "unsubscribe" webhook → set `newsletter_opt_in = False` or `newsletter_unsubscribed_at` in CRM.

### Provider setup
- **Mailchimp:** List → Settings → Webhooks; add URL + optional secret; subscribe to Subscribe (and optionally Profile update, Unsubscribe).
- **Constant Contact:** Configure webhook for contact added/updated; use their docs for payload and signature verification.

---

## 2. Outbound: CRM → Mailchimp / Constant Contact (Newsletters)

### Flow
- Selected people in CRM (e.g. opted-in Clients/Leads) are pushed to a list in Mailchimp or Constant Contact for sending newsletters.

### Requirements
- **Credentials (env/settings):**
  - **Mailchimp:** API key, Audience (list) ID.
  - **Constant Contact:** API key, secret, OAuth2 access + refresh tokens.
- **Outbound service:** Module that calls provider REST API to add/update list members by email. Map CRM `first_name`, `last_name`, `email`, `phone`, address → provider merge fields (FNAME, LNAME, PHONE, etc.).
- **Who to sync:** Define rule, e.g. only records with `newsletter_opt_in = True` (recommended for compliance). Models: Client, Lead, optionally Contact.
- **When to sync:** Option A) "Sync to Mailchimp" button/page. Option B) On save (post_save signal). Option C) Scheduled job (e.g. daily).
- **Idempotency:** Add-or-update by email so re-sync doesn't create duplicates. Optionally store provider ID (e.g. `mailchimp_subscriber_id`) on model for cleaner updates.

---

## 3. Data Model Additions (Recommended)

| Field / concept | Model(s) | Purpose |
|-----------------|----------|--------|
| `newsletter_opt_in` | Client, Lead (optional: Contact) | Only sync to email platform when True; compliance. |
| `mailchimp_subscriber_id` / `constant_contact_id` | Client, Lead (or shared "email marketing" link table) | Track which CRM record maps to which subscriber; support updates. |
| `newsletter_unsubscribed_at` or use `newsletter_opt_in = False` | Same | Reflect unsubscribe from webhook in CRM. |

---

## 4. Architecture (High Level)

```
CRM (Django)
  • Client, Lead, Contact
  • Optional: newsletter_opt_in, provider id, unsubscribed flag
       │
       ├── Outbound: REST API → add/update list member (newsletters)
       └── Inbound:  Webhooks ← subscribe / unsubscribe / profile update
       │
       ▼
Mailchimp or Constant Contact
  • Lists, merge fields, webhooks
  • Website form → signup → webhook → CRM creates/updates Lead
```

---

## 5. Implementation Checklist

### Inbound (platform → CRM)
- [ ] Webhook URL route(s) and view(s); POST only; CSRF-exempt.
- [ ] Verify Mailchimp/Constant Contact webhook signature or secret.
- [ ] Parse payload → create/update Lead (and optionally newsletter status).
- [ ] Handle subscribe; optionally handle unsubscribe and profile update.
- [ ] Return 200 so provider doesn't retry unnecessarily.
- [ ] Configure webhooks in Mailchimp/Constant Contact dashboard.

### Outbound (CRM → platform)
- [ ] Store API key and list ID (Mailchimp) or OAuth2 tokens (Constant Contact) in env/settings.
- [ ] Implement service/helper: add or update subscriber by email.
- [ ] Define sync rule (e.g. `newsletter_opt_in=True`).
- [ ] UI: "Sync to Mailchimp" / "Sync to Constant Contact" (and/or per-record "Add to newsletter").
- [ ] Optional: store provider subscriber ID on model; optional scheduled sync job.

### Data model
- [ ] Add `newsletter_opt_in` to Client (and Lead, optionally Contact) if syncing only opted-in.
- [ ] Optional: add provider ID and unsubscribe timestamp/flag for 2-way consistency.

### Security & ops
- [ ] Never commit API keys or webhook secrets; use environment variables.
- [ ] Log webhook failures and sync errors for debugging.

---

## 6. Provider Choice

- Implement one provider first (e.g. Mailchimp); same pattern applies for Constant Contact later.
- Mailchimp: simpler API (API key + list ID). Constant Contact: OAuth2 required for API access.
