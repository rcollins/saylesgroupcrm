"""
Vercel serverless entry point for Django (WSGI).
Used by @ardnt/vercel-python-wsgi builder. Expose the app as "application".
"""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

from recrmapp.wsgi import application  # noqa: E402
