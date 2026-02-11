import os
from django.core.wsgi import get_wsgi_application
from whitenoise.middleware import WhiteNoiseMiddleware # Import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

application = get_wsgi_application()

# Wrap your application with WhiteNoise
application = WhiteNoiseMiddleware(application, root=os.path.join(os.path.dirname(__file__), 'staticfiles'))

app = application  # Important: Vercel needs this variable
