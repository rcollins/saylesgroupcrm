#!/usr/bin/env bash
# Run this during Vercel build so admin (and app) static files are collected.
# In Vercel: Settings → General → Build Command = "bash build.sh" (or "python manage.py collectstatic --noinput")
set -e
echo "Running collectstatic..."
python manage.py collectstatic --noinput --clear
echo "Collectstatic done. staticfiles at: $(pwd)/staticfiles"
ls -la staticfiles/ | head -20
