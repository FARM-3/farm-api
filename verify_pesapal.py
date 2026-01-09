import os
import django
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
django.setup()

from django.conf import settings
from payments.services.pesapal import get_pesapal_access_token

def verify():
    print("--- Pesapal Verification ---")
    key = getattr(settings, 'PESAPAL_CONSUMER_KEY', None)
    secret = getattr(settings, 'PESAPAL_CONSUMER_SECRET', None)
    base_url = getattr(settings, 'PESAPAL_BASE_URL', None)

    print(f"Base URL: {base_url}")
    print(f"Consumer Key: {key[:4] if key else 'None'}...{key[-4:] if key else ''}")
    print(f"Consumer Secret: {'Set' if secret else 'Not Set'}")

    if not key or not secret:
        print("ERROR: Credentials missing in settings.")
        return

    print("\nAttempting to get access token...")
    try:
        token = get_pesapal_access_token()
        print(f"SUCCESS: Token received! (Length: {len(token)})")
        print(f"Token preview: {token[:20]}...")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    verify()
