import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nursing_center.settings')
django.setup()

from firebase_admin import auth
import firebase_admin

try:
    # This will fail because the token is junk, but we want to see if it even runs without a "Project ID" error.
    auth.verify_id_token("junk_token")
except ValueError as e:
    # Expected: "ID token must be a non-empty string." or similar
    print(f"Caught expected ValueError: {e}")
except Exception as e:
    print(f"Caught exception: {type(e).__name__} - {e}")
