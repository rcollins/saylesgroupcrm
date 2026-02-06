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

## Sample data (optional)

Management commands to load sample data:

```bash
cd recrmapp
python manage.py load_sample_clients
python manage.py load_sample_contacts
python manage.py load_sample_leads
python manage.py load_sample_properties
python manage.py load_sample_transactions
```

## License

Use as needed for your project.
