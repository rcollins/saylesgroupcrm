# Vercel NOT_FOUND (404) for Django — Correct Setup

**Use the official Vercel Python runtime.** Do not use third-party WSGI builders.

---

## 1. Correct configuration

### vercel.json

Use **`@vercel/python`** (official). No `package.json` or npm packages.

```json
{
  "version": 2,
  "builds": [
    {
      "src": "index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "index.py"
    }
  ]
}
```

- **Builder:** `@vercel/python` — official, supports WSGI (Django/Flask) and ASGI.
- **Route dest:** `"index.py"` (with or without leading `/`).

### index.py (entry point)

- Add project root to `sys.path` so `recrmapp` is importable when Vercel runs the function.
- Expose **`app`** (or `application`). The runtime detects a WSGI callable and wraps it.

```python
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

from recrmapp.wsgi import application

app = application  # Vercel looks for 'app' or 'application' and wraps WSGI
```

### What you do **not** need

- **No** `package.json` for Python-only Django on Vercel.
- **No** `@ardnt/vercel-python-wsgi` or other third-party WSGI builders.
- **No** npm install step for this deployment.

---

## 2. Why NOT_FOUND usually happens (Django on Vercel)

Common causes, in order of likelihood:

1. **Environment variables missing in Vercel**  
   Set in Project → Settings → Environment Variables:
   - `SECRET_KEY`
   - `DATABASE_URL` (Postgres; SQLite is not suitable for serverless)
   - `DEBUG=False`
   - `ALLOWED_HOSTS` if you override in settings (e.g. `.vercel.app,.now.sh`)

2. **ALLOWED_HOSTS**  
   Must include your Vercel host (e.g. `.vercel.app`). Already set in this project.

3. **Database**  
   Use a hosted Postgres (e.g. Vercel Postgres, Neon, Supabase). SQLite does not work reliably on Vercel serverless.

4. **Root Directory**  
   In Vercel → Settings → General, **Root Directory** should be the folder that contains `index.py`, `vercel.json`, `manage.py`, and `recrmapp/`. Often `.` (repo root) or a single subfolder (e.g. `recrmapp`).

5. **Build or runtime errors**  
   Check **Build** and **Function** logs in the Vercel dashboard for import errors, missing deps, or Django startup errors.

---

## 3. Mental model

- **NOT_FOUND** = Vercel has no resource or function for that URL (or the function failed to start).
- **`@vercel/python`** can run WSGI apps: it looks for `app` / `application` in the entry file and wraps them. You do not need a separate WSGI builder.
- One entry file (`index.py`) → one serverless function; routing sends all paths to it, and Django’s URLconf handles the path.

---

## 4. Checklist before blaming routing

- [ ] `vercel.json` uses `"use": "@vercel/python"` and `"dest": "index.py"`.
- [ ] `index.py` adds project root to `sys.path` and exposes `app = application`.
- [ ] `ALLOWED_HOSTS` includes `.vercel.app` (or your domain).
- [ ] Env vars set in Vercel: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`.
- [ ] Database is Postgres (not SQLite).
- [ ] Root Directory points at the folder that contains `index.py` and `vercel.json`.
- [ ] Build succeeds; check Function logs for Django errors.

---

## 5. References

- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python) — official docs.
- [Django on Vercel template](https://vercel.com/templates/python/django-hello-world) — official example.

---

*This doc was updated to follow Vercel’s official guidance and remove incorrect advice about third-party WSGI builders and package.json.*
