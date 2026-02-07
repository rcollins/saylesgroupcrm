# RE CRM

A Django-based real estate CRM for managing clients, leads, properties, contacts, and transactions.

## Features

- **Dashboard** — Summary stats and income/sales charts (Buyer vs Seller vs Dual)
- **Clients** — Full CRUD, notes, filters, and search
- **Leads** — Track and convert leads to clients
- **Properties** — Listings with notes and multiple photo uploads
- **Contacts** — Vendors, lenders, agents, and other contacts with notes
- **Transactions** — Deals with parties, milestones, tasks, and notes
- **Authentication** — Sign up, log in, logout, and password change
- **App Admin** — Custom settings (app name, logo, chart colors, editable status/type lists); staff-only, separate from Django admin
- **Email** — Send email from Client and Contact detail pages (Anymail + Resend)

## Requirements

- Python 3.10+
- See [requirements.txt](requirements.txt) for dependencies

## Setup

1. **Clone and enter the project** (if applicable), then create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables** — Create a `.env` file in the project root (same directory as this README). Required:

   ```env
   SECRET_KEY=your-secret-key-here
   ```

   Optional (with defaults as noted):

   ```env
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost,testserver
   RESEND_API_KEY=re_...          # Optional: Anymail/Resend; if omitted, emails print to console
   DEFAULT_FROM_EMAIL=...        # Optional when using Resend; defaults to onboarding@resend.dev
   DATABASE_URL=postgresql://user:pass@host/dbname
   ```

   - If `DATABASE_URL` is set, PostgreSQL is used; otherwise SQLite is used (`db.sqlite3` in the app directory).

4. **Run migrations** (from the directory that contains `manage.py`):

   ```bash
   cd recrmapp
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for Django admin and App Admin):

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

   Open http://127.0.0.1:8000/ in your browser.

## Project layout

- `recrmapp/` — Django project root
  - `recrmapp/` — Settings (`settings.py`), URLs, WSGI/ASGI
  - `crm/` — Main app: models, views, forms, templates, migrations
  - `manage.py`
- `requirements.txt` — Python dependencies
- `.env` — Local environment config (not committed; see `.gitignore`)

## Email (Anymail + Resend)

If `RESEND_API_KEY` is set in `.env`, the app sends real email via [Resend](https://resend.com/). Otherwise, the default backend is the console (messages are printed in the terminal).

- **Send email from the app:** Open a Client or Contact that has an email address; use the “Send email” card to compose and send.
- **Test configuration:** `python manage.py send_test_email you@example.com`

## Sample data (optional)

Management commands load fictional data with **varying statuses** (and types where applicable). Run in this order so transactions can link to properties and clients:

| Command | Count | Variety |
|---------|-------|---------|
| `load_sample_leads` | 10 | new, attempted, in_progress, connected, unqualified, bad_timing |
| `load_sample_clients` | 15 | potential, active, closed, lost, inactive; buyer/seller/both |
| `load_sample_contacts` | 20 | lender, agent, title_company, inspector, attorney, vendor, other |
| `load_sample_properties` | 15 | available, under_contract, sold, off_market; multiple property types |
| `load_sample_transactions` | 8 | active, under_contract, closed; buyer, seller, dual representation |

```bash
cd recrmapp
python manage.py load_sample_clients --clear    # optional: replace existing sample data
python manage.py load_sample_contacts --clear
python manage.py load_sample_leads --clear
python manage.py load_sample_properties --clear
python manage.py load_sample_transactions --clear
```

## License

Use as needed for your project.
