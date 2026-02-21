from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response, status, Cookie
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.db.session import get_db
from app.models import User, RefreshToken
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)):
    existing = await db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=payload.email, password_hash=get_password_hash(payload.password))
    db.add(user)
    await db.flush()

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(token_record)
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    return AuthResponse(user=UserResponse(id=user.id, email=user.email), tokens=TokenResponse(access_token=access_token))


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(refresh_token),
        expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(token_record)
    await db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        samesite="lax",
        secure=False,
    )

    return AuthResponse(user=UserResponse(id=user.id, email=user.email), tokens=TokenResponse(access_token=access_token))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    tokens = (await db.execute(select(RefreshToken).where(RefreshToken.expires_at > datetime.utcnow()))).scalars().all()
    matched = None
    for token in tokens:
        if verify_password(refresh_token, token.token_hash):
            matched = token
            break

    if not matched:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return TokenResponse(access_token=create_access_token(matched.user_id))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, db: AsyncSession = Depends(get_db), refresh_token: str | None = Cookie(default=None)):
    if refresh_token:
        tokens = (await db.execute(select(RefreshToken))).scalars().all()
        for token in tokens:
            if verify_password(refresh_token, token.token_hash):
                await db.delete(token)
        await db.commit()

    response.delete_cookie("refresh_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
