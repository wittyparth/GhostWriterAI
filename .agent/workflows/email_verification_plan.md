---
description: Implementation plan for email verification using Resend
---

# Email Verification Implementation Plan

## Overview
Secure the user registration process by determining email ownership before allowing full access. We will use [Resend](https://resend.com/) for sending emails.

## Architecture

### 1. Database Changes
- **Target File**: `backend/src/database/models.py`
- **Model**: `User`
- **Changes**:
    - Add `is_verified` (Boolean, default False)
    - Add `verification_token` (String, nullable) - Stores the token sent to email
    - Add `verification_token_expires_at` (DateTime, nullable)

### 2. Backend Config & Utilities
- **Target File**: `backend/src/config/settings.py` (or similar)
    - Add `RESEND_API_KEY`
    - Add `FROM_EMAIL` (e.g., `onboarding@resend.dev` or your domain)
- **New Utility**: `backend/src/services/email.py`
    - Function `send_verification_email(to_email: str, token: str, name: str)`
    - Uses Resend SDK to send HTML email with verification link.

### 3. Backend API Routes
- **Target File**: `backend/src/api/routes/auth.py`
    - **Modify `/register`**:
        - Generate unique token (UUID or random string).
        - Set `is_verified = False`.
        - Store token and expiry in DB.
        - Call `send_verification_email`.
        - Prevent immediate login (or allow restricted access).
    - **New Endpoint `POST /verify-email`**:
        - Input: `{ "token": "..." }`
        - Logic: Find user by token. Check expiry. Set `is_verified = True`, clear token.
        - Return: Success message + Auto-login tokens (optional but better UX).
    - **Modify `/login`**:
        - Check if `is_verified` is True.
        - If False, return 403 with "Email not verified".
    - **New Endpoint `POST /resend-verification`**:
        - Input: `{ "email": "..." }`
        - Logic: Generate new token, update DB, resend email.

### 4. Frontend Changes
- **New Page**: `frontend/src/pages/VerifyEmailPage.tsx`
    - Route: `/verify-email` (Users land here from the email link)
    - Logic: Grab `token` from URL query params. Call `verify-email` API. Show success/error state.
- **Modify `SignupPage.tsx`**:
    - After detailed success, show "Check your email" state/message instead of redirecting to Dashboard immediately.
- **Modify `LoginPage.tsx`**:
    - Handle "Email not verified" error. Show "Resend Verification" button/link if that error occurs.

## Execution Steps

1.  **Dependencies**: Install `resend` python package.
2.  **Database**: Update `User` model and run migrations (if using Alembic) or rely on auto-sync (if applicable).
    - *Note*: We'll assume direct SQLAlchemy model updates for this context unless migration scripts are visible.
3.  **Utility**: Implement `EmailService` with Resend.
4.  **Backend API**: Update Auth routes.
5.  **Frontend**: Create Verification Page and update Sign Up/Login flows.
6.  **Testing**: Verify flow end-to-end.

## Configuration
- User needs to provide `RESEND_API_KEY` in `.env`.
