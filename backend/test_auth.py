import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bigredmacro.settings")
django.setup()
from api.services.calendar_api import get_authorization_url
url, state, verifier = get_authorization_url("http://localhost:5173/calendar-callback")
print(f"URL: {url}")
