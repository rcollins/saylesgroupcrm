import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

application = get_wsgi_application()
app = application  # Important: Vercel needs this variable
