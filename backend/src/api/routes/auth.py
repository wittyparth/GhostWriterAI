"""
Authentication API routes with JWT tokens.

Provides endpoints for:
- User registration
- User login
- Google login
- Token refresh
- Get current user
- Logout
"""

import logging
import bcrypt
import jwt
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from google.oauth2 import id_token
from google.auth.transport import requests

from src.database import get_session
from src.database.models import User, BrandProfile
from src.config.settings import get_settings
from src.services.email import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

security = HTTPBearer()
settings = get_settings()

# JWT Configuration
JWT_SECRET = settings.jwt_secret if hasattr(settings, 'jwt_secret') else "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
REFRESH_TOKEN_EXPIRE_DAYS = 7


# ============ Request/Response Schemas ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: datetime
    has_brand_profile: bool


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    linkedin_profile_url: Optional[str] = None


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


# ============ Utility Functions ============

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    """Create a JWT access token."""
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create a JWT refresh token."""
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    stmt = select(User).where(User.user_id == UUID(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """Dependency to optionally get the current user."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, session)
    except HTTPException:
        return None


# ============ API Endpoints ============

@router.post("/register")
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user account.
    """
    # Check if email already exists
    stmt = select(User).where(User.email == request.email)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification token
    verification_token = uuid4().hex
    token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    # Create user with hashed password
    user = User(
        name=request.name,
        email=request.email,
        linkedin_profile_url=hash_password(request.password),
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires_at=token_expiry
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Send verification email
    try:
        email_service = EmailService()
        await email_service.send_verification_email(
            to_email=user.email,
            name=user.name,
            token=verification_token,
            frontend_url=settings.frontend_url
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {e}")
        # We don't fail registration, just log error
        
    logger.info(f"New user registered: {user.email}")
    
    return {"message": "Registration successful. Please check your email to verify your account."}


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Login with email and password.
    """
    # Find user by email
    stmt = select(User).where(User.email == request.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    # Check if verified
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox."
        )
    
    # Verify password
    stored_password = user.linkedin_profile_url
    if not stored_password or not verify_password(request.password, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate tokens
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))
    
    # Check if user has brand profile
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    has_brand_profile = result.scalar_one_or_none() is not None
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "has_brand_profile": has_brand_profile,
        }
    )


@router.post("/verify-email", response_model=TokenResponse)
async def verify_email(
    request: VerifyEmailRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Verify email address using token.
    """
    stmt = select(User).where(User.verification_token == request.token)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
        
    if user.verification_token_expires_at and user.verification_token_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired"
        )
        
    # Mark as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires_at = None
    
    await session.commit()
    await session.refresh(user)
    
    # Generate tokens for auto-login
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))
    
    # Check if user has brand profile
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    has_brand_profile = result.scalar_one_or_none() is not None
    
    logger.info(f"Email verified for user: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "has_brand_profile": has_brand_profile,
        }
    )


@router.post("/resend-verification")
async def resend_verification(
    request: ResendVerificationRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Resend verification email.
    """
    stmt = select(User).where(User.email == request.email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if user exists
        return {"message": "If account exists, verification email sent."}
        
    if user.is_verified:
        return {"message": "Account already verified."}
        
    # Generate new token
    verification_token = uuid4().hex
    token_expiry = datetime.utcnow() + timedelta(hours=24)
    
    user.verification_token = verification_token
    user.verification_token_expires_at = token_expiry
    
    await session.commit()
    
    # Send email
    try:
        email_service = EmailService()
        await email_service.send_verification_email(
            to_email=user.email,
            name=user.name,
            token=verification_token,
            frontend_url=settings.frontend_url
        )
    except Exception as e:
        logger.error(f"Failed to resend verification email: {e}")
        
    return {"message": "Verification email sent."}


@router.get("/google/login")
async def google_login_redirect():
    """
    Initiate Google OAuth flow.
    Redirects user to Google's consent screen.
    """
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    # Build Google OAuth URL
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    redirect_url = f"{google_auth_url}?{query_string}"
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=redirect_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Handle Google OAuth callback.
    Exchanges authorization code for tokens and creates/logs in user.
    Redirects to frontend with JWT tokens.
    """
    import httpx
    
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    try:
        # Exchange authorization code for tokens
        token_url = "https://oauth2.googleapis.com/token"
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            
            if token_response.status_code != 200:
                logger.error(f"Google token exchange failed: {token_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to exchange authorization code"
                )
            
            token_data = token_response.json()
            google_access_token = token_data.get("access_token")
            
            # Get user info from Google
            userinfo_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"}
            )
            
            if userinfo_response.status_code != 200:
                logger.error(f"Failed to get user info: {userinfo_response.text}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Failed to get user information"
                )
            
            user_info = userinfo_response.json()
            email = user_info.get("email")
            name = user_info.get("name", "")
            
            if not email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not provided by Google"
                )
        
        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            random_pass = bcrypt.hashpw(uuid4().hex.encode(), bcrypt.gensalt()).decode()
            
            user = User(
                name=name,
                email=email,
                linkedin_profile_url=random_pass,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"New user registered via Google: {email}")
        else:
            logger.info(f"User logged in via Google: {email}")
        
        # Generate JWT tokens
        access_token = create_access_token(str(user.user_id))
        refresh_token = create_refresh_token(str(user.user_id))
        
        # Redirect to frontend with tokens in URL params
        from fastapi.responses import RedirectResponse
        from urllib.parse import urlencode
        
        frontend_callback_url = f"{settings.frontend_url}/auth/callback"
        params = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
        }
        redirect_url = f"{frontend_callback_url}?{urlencode(params)}"
        
        return RedirectResponse(url=redirect_url)
        
    except httpx.RequestError as e:
        logger.error(f"Network error during Google auth: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Network error during authentication"
        )
    except Exception as e:
        logger.error(f"Google login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/google", response_model=TokenResponse)
async def google_login_token(
    request: GoogleLoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Login with Google ID token (for popup flow).
    This is an alternative to the redirect flow.
    """
    try:
        # Verify Google ID token
        id_info = id_token.verify_oauth2_token(
            request.token,
            requests.Request(),
            settings.google_client_id
        )
        
        email = id_info['email']
        name = id_info.get('name', '')
        
        # Check if user exists
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            random_pass = bcrypt.hashpw(uuid4().hex.encode(), bcrypt.gensalt()).decode()
            
            user = User(
                name=name,
                email=email,
                linkedin_profile_url=random_pass,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"New user registered via Google: {email}")
        else:
            logger.info(f"User logged in via Google: {email}")
        
        # Generate tokens
        access_token = create_access_token(str(user.user_id))
        refresh_token = create_refresh_token(str(user.user_id))
        
        # Check if user has brand profile
        stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
        result = await session.execute(stmt)
        has_brand_profile = result.scalar_one_or_none() is not None
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "user_id": str(user.user_id),
                "email": user.email,
                "name": user.name,
                "created_at": user.created_at.isoformat(),
                "has_brand_profile": has_brand_profile,
            }
        )
        
    except ValueError as e:
        logger.warning(f"Invalid Google token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token"
        )
    except Exception as e:
        logger.error(f"Google login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Refresh access token using a refresh token.
    """
    payload = decode_token(request.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    # Verify user still exists
    stmt = select(User).where(User.user_id == UUID(user_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Generate new tokens
    access_token = create_access_token(str(user.user_id))
    new_refresh_token = create_refresh_token(str(user.user_id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
        }
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get the current authenticated user's profile.
    """
    # Check if user has brand profile
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    has_brand_profile = result.scalar_one_or_none() is not None
    
    return UserResponse(
        user_id=str(user.user_id),
        email=user.email or "",
        name=user.name,
        created_at=user.created_at,
        has_brand_profile=has_brand_profile,
    )


@router.patch("/me")
async def update_me(
    request: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Update the current user's profile.
    """
    if request.name:
        user.name = request.name
    
    await session.commit()
    
    return {
        "user_id": str(user.user_id),
        "email": user.email,
        "name": user.name,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }



class UsageResponse(BaseModel):
    posts_used_today: int
    daily_limit: int
    credits_remaining: int


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get the current user's daily usage.
    """
    from src.database.repositories.base import PostRepository
    post_repo = PostRepository(session)
    count = await post_repo.count_today(user.user_id)
    
    # Determine limit based on tier
    limit = settings.free_tier_daily_limit
    if getattr(user, "subscription_tier", "free") == "premium":
        limit = 1000  # Premium limit
    
    return UsageResponse(
        posts_used_today=count,
        daily_limit=limit,
        credits_remaining=max(0, limit - count),
    )

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard tokens).
    """
    return {"message": "Logged out successfully"}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Change the current user's password.
    
    Requires current password for verification.
    """
    # Verify current password
    stored_password = user.linkedin_profile_url  # Using this field for password hash
    if not stored_password or not verify_password(request.current_password, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Hash and store new password
    user.linkedin_profile_url = hash_password(request.new_password)
    await session.commit()
    
    logger.info(f"Password changed for user {user.user_id}")
    
    return {"message": "Password changed successfully"}


class DeleteAccountRequest(BaseModel):
    password: str
    confirm: bool = Field(..., description="Must be true to confirm deletion")


@router.delete("/account")
async def delete_account(
    request: DeleteAccountRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Permanently delete the current user's account.
    
    This action cannot be undone. Requires password confirmation.
    """
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please confirm account deletion by setting confirm to true"
        )
    
    # Verify password
    stored_password = user.linkedin_profile_url
    if not stored_password or not verify_password(request.password, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
        )
    
    # Delete user's brand profile first (if exists)
    stmt = select(BrandProfile).where(BrandProfile.user_id == user.user_id)
    result = await session.execute(stmt)
    profile = result.scalar_one_or_none()
    if profile:
        await session.delete(profile)
    
    # Delete user (cascades to other related data)
    await session.delete(user)
    await session.commit()
    
    logger.info(f"Account deleted for user {user.user_id}")
    
    return {"message": "Account deleted successfully"}
