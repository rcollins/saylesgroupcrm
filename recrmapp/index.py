import os
import sys

# Ensure project root is on Python path (Vercel serverless may run from a different cwd)
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

from recrmapp.wsgi import application  # noqa: E402

# @vercel/python looks for 'app' or 'application' and wraps WSGI automatically
app = application

