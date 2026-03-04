from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Tuple

import jwt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.core.security_log import log_refresh_token_reuse
from app.models.user import User, RefreshToken
from app.schemas.auth import TokenResponse, UserResponse

# Basic protection against brute force; you can tune these.
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _hash_refresh_token(token: str) -> str:
    """
    Hash refresh tokens before storing.
    SHA-256 is fine here; tokens are high entropy.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Tuple[UserResponse, TokenResponse]:
    """
    Register a new user, hash password with Argon2,
    and issue initial access + refresh tokens.
    """
    normalized_email = email.strip().lower()

    existing = await _get_user_by_email(db, normalized_email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered.",
        )

    user = User(
        email=normalized_email,
        password_hash=hash_password(password),
    )
    db.add(user)

    # Flush so we get user.id without committing (get_db will commit).
    await db.flush()
    await db.refresh(user)

    access_token = create_access_token(str(user.id), user.role)
    refresh_token, _jti = create_refresh_token(str(user.id))

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh_token(refresh_token),
        expires_at=_now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)

    user_out = UserResponse.model_validate(user)
    tokens_out = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    return user_out, tokens_out


async def _check_account_lock(user: User) -> None:
    now = _now_utc()
    if user.locked_until and user.locked_until > now:
        # Do NOT reveal exact time in detail if you want less info leakage.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked. Try again later.",
        )


async def _handle_failed_login(user: User) -> None:
    now = _now_utc()
    user.failed_attempts += 1
    if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User:
    """
    Validate credentials, enforce lockout, and normalize email.
    Raises HTTPException on failure.
    """
    normalized_email = email.strip().lower()
    user = await _get_user_by_email(db, normalized_email)

    # Intentionally generic error messages to avoid leaking whether
    # the email exists.
    invalid_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password.",
    )

    if not user:
        # Optional: run a dummy verify to normalize timing.
        raise invalid_exc

    await _check_account_lock(user)

    if not verify_password(password, user.password_hash):
        await _handle_failed_login(user)
        raise invalid_exc

    # Successful login: reset lock state.
    user.failed_attempts = 0
    user.locked_until = None
    return user


async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Tuple[UserResponse, TokenResponse]:
    """
    Login user, enforce lockout, and issue fresh access + refresh tokens.
    """
    user = await authenticate_user(db, email, password)

    access_token = create_access_token(str(user.id), user.role)
    refresh_token, _jti = create_refresh_token(str(user.id))

    refresh_record = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh_token(refresh_token),
        expires_at=_now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_record)

    user_out = UserResponse.model_validate(user)
    tokens_out = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    return user_out, tokens_out


async def rotate_refresh_token(
    db: AsyncSession,
    refresh_token: str,
) -> TokenResponse:
    """
    Implement refresh token rotation and basic reuse detection.

    - Verify JWT & type=refresh.
    - Find stored token_hash and ensure not revoked/expired.
    - Revoke current row.
    - Issue new access + refresh and store new hash.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token.",
        )

    try:
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token type.",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload.",
        )

    token_hash = _hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored: RefreshToken | None = result.scalar_one_or_none()
    now = _now_utc()

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
        )

    if stored.revoked:
        from sqlalchemy import update

        log_refresh_token_reuse(str(stored.user_id))
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == stored.user_id)
            .values(revoked=True)
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token was reused. All sessions have been revoked. Please log in again.",
        )

    if stored.expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
        )

    # One-time use: revoke this token
    stored.revoked = True

    result_user = await db.execute(select(User).where(User.id == stored.user_id))
    user = result_user.scalar_one_or_none()
    role = user.role if user else "user"

    # Issue new pair.
    access_token = create_access_token(user_id, role)
    new_refresh_token, _new_jti = create_refresh_token(user_id)

    new_stored = RefreshToken(
        user_id=stored.user_id,
        token_hash=_hash_refresh_token(new_refresh_token),
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_stored)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


async def list_sessions(
    db: AsyncSession,
    user_id: str,
    current_refresh_token: str | None = None,
) -> list[dict]:
    """
    List active (non-revoked, non-expired) refresh tokens for the user.
    Optionally mark the session matching current_refresh_token as is_current.
    """
    now = _now_utc()
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        .order_by(RefreshToken.created_at.desc())
    )
    tokens = result.scalars().all()
    current_hash = (
        _hash_refresh_token(current_refresh_token) if current_refresh_token else None
    )
    return [
        {
            "id": str(t.id),
            "created_at": t.created_at,
            "expires_at": t.expires_at,
            "is_current": current_hash == t.token_hash if current_hash else False,
        }
        for t in tokens
    ]


async def revoke_session_by_id(
    db: AsyncSession,
    session_id: str,
    user_id: str,
) -> None:
    """
    Revoke a specific refresh token (session) if it belongs to the user.
    Raises HTTPException if not found or not owned.
    """
    from uuid import UUID

    try:
        uid = UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.id == uid,
            RefreshToken.user_id == user_id,
        )
    )
    stored: RefreshToken | None = result.scalar_one_or_none()
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found.",
        )
    stored.revoked = True


async def logout_user(
    db: AsyncSession,
    refresh_token: str | None,
) -> None:
    """
    Revoke a single refresh token (current device).
    If token is missing or already invalid, this is a no-op.
    """
    if not refresh_token:
        return

    token_hash = _hash_refresh_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored: RefreshToken | None = result.scalar_one_or_none()
    if stored and not stored.revoked:
        stored.revoked = True
