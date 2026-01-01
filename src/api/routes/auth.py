"""
Authentication API routes with JWT tokens.

Provides endpoints for:
- User registration
- User login
- Token refresh
- Get current user
- Logout
"""

import logging
import bcrypt
import jwt
from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.database.models import User, BrandProfile
from src.config.settings import get_settings

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

@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Register a new user account.
    
    Returns access and refresh tokens upon successful registration.
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
    
    # Create user with hashed password
    # Note: In the current model, we don't have a password field
    # We'll store the hashed password in a new field or use linkedin_profile_url temporarily
    user = User(
        name=request.name,
        email=request.email,
        linkedin_profile_url=hash_password(request.password),  # Store hashed password
    )
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Generate tokens
    access_token = create_access_token(str(user.user_id))
    refresh_token = create_refresh_token(str(user.user_id))
    
    logger.info(f"New user registered: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "user_id": str(user.user_id),
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Login with email and password.
    
    Returns access and refresh tokens upon successful authentication.
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
    
    # Verify password (stored in linkedin_profile_url for now)
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


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client should discard tokens).
    
    Note: For full security, implement token blacklisting.
    """
    return {"message": "Logged out successfully"}
