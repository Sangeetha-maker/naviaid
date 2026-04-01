"""
NaviAid Auth Router – JWT register/login + Google OAuth stub.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from app import crud, schemas
from app.auth_utils import verify_password, create_access_token, decode_token
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/register", response_model=schemas.TokenResponse, status_code=201)
async def register(data: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    email_lower = data.email.lower()
    existing = await crud.get_user_by_email(db, email_lower)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await crud.create_user(db, email_lower, data.password, data.name)
    token = create_access_token({"sub": user.id, "role": user.role})
    return schemas.TokenResponse(access_token=token, user_id=user.id, role=user.role)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    email_lower = data.email.lower()
    user = await crud.get_user_by_email(db, email_lower)
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    token = create_access_token({"sub": user.id, "role": user.role})
    return schemas.TokenResponse(access_token=token, user_id=user.id, role=user.role)


@router.get("/me", response_model=schemas.UserOut)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_current_user(credentials, db)
    profile = await crud.get_profile(db, user.id)
    return schemas.UserOut.from_user_and_profile(user, profile)


@router.get("/google")
async def google_login():
    """Stub – returns instructions for OAuth setup."""
    return {
        "message": "Google OAuth – set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env",
        "redirect_url": "https://accounts.google.com/o/oauth2/v2/auth",
    }


# ────────────── Shared Dependency ──────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    return await _get_current_user(credentials, db)


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    user = await _get_current_user(credentials, db)
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


async def _get_current_user(credentials, db):
    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
