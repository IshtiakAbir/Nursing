# Firebase Authentication Setup Guide

## Step 1 — Create a Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** → give it a name (e.g. `premier-medical-institute`)
3. Continue through the setup wizard (you can disable Google Analytics if you want)

---

## Step 2 — Enable Authentication Providers

1. In the Firebase Console, open your project
2. Navigate to **Build → Authentication**
3. Click the **"Sign-in method"** tab
4. Enable:
   - **Email/Password** — toggle ON
   - **Google** — toggle ON, enter your project's support email, Save

---

## Step 3 — Download the Service Account Key (for Django backend)

1. In the Firebase Console, go to **Project Settings** (⚙️ gear icon)
2. Click the **"Service accounts"** tab
3. Click **"Generate new private key"** → **Confirm**
4. A JSON file will be downloaded. Rename it to:
   ```
   firebase-service-account.json
   ```
5. Place it in your project's **root directory** (same folder as `manage.py`):
   ```
   c:\xxampp\htdocs\Nursing\firebase-service-account.json
   ```

> ⚠️ **IMPORTANT**: Add `firebase-service-account.json` to your `.gitignore` to keep it secret!

---

## Step 4 — Get Your Web App Config (for the frontend JavaScript)

1. In the Firebase Console, go to **Project Settings** (⚙️ gear icon)
2. Scroll to the **"Your apps"** section
3. Click **"Add app"** → choose the **Web** icon (`</>`)
4. Give it a nickname (e.g. `Premier Institute Web`) → Register app
5. Copy the `firebaseConfig` object that looks like:
   ```js
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "your-project.firebaseapp.com",
     projectId: "your-project",
     storageBucket: "your-project.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123",
   };
   ```

6. Open **both** files and replace the placeholder config:
   - `templates/login.html` — find `// ── YOUR FIREBASE WEB APP CONFIG` and replace
   - `templates/register.html` — same section

---

## Step 5 — Update `.env`

Open `.env` and set your Firebase Project ID:

```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_KEY=firebase-service-account.json
```

---

## Step 6 — Add Authorized Domains (for Google Sign-In)

1. In Firebase Console → Authentication → **Settings** tab → **Authorized domains**
2. Make sure `localhost` is listed (it should be by default)
3. If your site has a live domain (e.g. `premier-institute.com`), add it here

---

## How It Works

### Login Flow
```
User fills email+password (or clicks Google)
  → Firebase SDK authenticates client-side
  → Frontend gets an ID Token from Firebase
  → Frontend POSTs idToken to /auth/firebase-login/
  → Django verifies the token with firebase-admin
  → If user exists and is verified → Django session created → redirect to /dashboard/
  → If user not found → redirect to /register/?firebase=1 (complete profile)
  → If pending verification → show message
```

### Registration Flow
```
User fills email+password OR clicks Google (Step 1)
  → Firebase creates the user account
  → Frontend gets ID Token
  → Step 2: User fills student profile (Reg No, Phone, Batch)
  → Frontend POSTs idToken + profile fields to /auth/firebase-register/
  → Django verifies token, creates User + StudentProfile (is_verified=False)
  → Success screen shown → admin must verify before login works
```

---

## Admin Verification

Students still need to be **verified by an admin** before they can log in.

1. Go to Django Admin: `/admin/`
2. Navigate to **Courses → Student profiles**
3. Find the new student, open their profile
4. Check **"Is verified"** and Save

---

## Existing Students (Django username/password)

If a student previously registered with a username/password (non-Firebase), they can still log in via Firebase **Email/Password** using the same email — the system will match them by email and update their username to `fb_<uid>` automatically.

---

## Security Notes

- The Firebase ID token is verified **server-side** using the `firebase-admin` SDK. The token cannot be forged.
- Django passwords for Firebase users are set to unusable (they cannot log in without Firebase)
- The service account JSON **must never be committed to git**
