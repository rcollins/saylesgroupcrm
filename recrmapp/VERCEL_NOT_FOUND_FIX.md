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

## 4. Media uploads (images) — avoid 500 on upload

Vercel’s filesystem is **read-only**. Saving uploads to `MEDIA_ROOT` fails and can cause 500 errors. Use **S3-compatible storage** in production.

1. Create a bucket (e.g. **AWS S3** or **Cloudflare R2**).
2. In Vercel → Project → Settings → Environment Variables, add:

   **Required for any S3-compatible backend:**
   - `AWS_STORAGE_BUCKET_NAME` — bucket name  
   - `AWS_ACCESS_KEY_ID` — access key  
   - `AWS_SECRET_ACCESS_KEY` — secret key  

   **For AWS S3:**
   - `AWS_S3_REGION_NAME` — e.g. `us-east-1`  

   **For Cloudflare R2 (S3-compatible):**
   - `AWS_S3_REGION_NAME` — use `auto`  
   - `AWS_S3_ENDPOINT_URL` — e.g. `https://<account_id>.r2.cloudflarestorage.com`  
   - (Optional) `AWS_S3_CUSTOM_DOMAIN` — custom domain for public URLs if you set one for the bucket  

3. Redeploy. Uploads (logo, property photos, signature image) will go to the bucket and URLs will point there.

---

## 5. Django admin theme / static files (CSS, JS) in production

With `DEBUG=False`, Django does not serve static files. This project uses **WhiteNoise** so the app serves its own static files (admin CSS/JS, etc.).

**Required:** Run `collectstatic` during the Vercel build so admin (and any app static files) get correct styling.

- In Vercel → Project → **Settings** → **General** → **Build & Development Settings**:
  - Set **Build Command** to:  
    `python manage.py collectstatic --noinput`  
  - (If your Root Directory is the repo root and the app lives in a subfolder, use e.g. `cd recrmapp && python manage.py collectstatic --noinput` so it runs from the folder that contains `manage.py`.)

Redeploy. The admin at `/admin/` should then load with the correct theme (no plain HTML, no black blocks).

- `STATIC_ROOT` is set to `staticfiles/` and WhiteNoise middleware is enabled in settings.

## 6. Checklist before blaming routing

- [ ] `vercel.json` uses `"use": "@vercel/python"` and `"dest": "index.py"`.
- [ ] `index.py` adds project root to `sys.path` and exposes `app = application`.
- [ ] **Build Command** runs `python manage.py collectstatic --noinput` (from the directory that has `manage.py`).
- [ ] `ALLOWED_HOSTS` includes `.vercel.app` (or your domain).
- [ ] Env vars set in Vercel: `SECRET_KEY`, `DATABASE_URL`, `DEBUG`.
- [ ] For image uploads: `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (and region/endpoint as above).
- [ ] Database is Postgres (not SQLite).
- [ ] Root Directory points at the folder that contains `index.py` and `vercel.json`.
- [ ] Build succeeds; check Function logs for Django errors.

---

## 7. References

- [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python) — official docs.
- [Django on Vercel template](https://vercel.com/templates/python/django-hello-world) — official example.

---

*This doc was updated to follow Vercel’s official guidance and remove incorrect advice about third-party WSGI builders and package.json.*
