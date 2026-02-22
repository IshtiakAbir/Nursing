import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nursing_center.settings')
django.setup()

import firebase_admin
from firebase_admin import auth

try:
    print(f"Firebase apps: {firebase_admin._apps}")
    # We can't verify a real token here easily without one,
    # but we can check if the app is initialized.
    if firebase_admin._apps:
        print("Firebase Admin SDK initialized successfully.")
        # Try to list users to check if credentials work
        page = auth.list_users()
        print("Successfully connected to Firebase Auth.")
    else:
        print("Firebase Admin SDK NOT initialized.")
except Exception as e:
    print(f"Error: {e}")
