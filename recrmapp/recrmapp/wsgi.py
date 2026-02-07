"""
WSGI config for recrmapp project.

It exposes the WSGI callable as a module-level variable named ``application``
(for local/other WSGI servers) and ``app`` (for Vercel serverless).
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

application = get_wsgi_application()
app = application
