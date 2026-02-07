import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recrmapp.settings')

from recrmapp.wsgi import application  # noqa: E402

app = application  # This line is critical for Vercel