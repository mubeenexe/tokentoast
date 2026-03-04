from __future__ import annotations

import asyncio
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_token
from app.models.user import User
from app.models.email_token import (
    EmailToken,
    EMAIL_TOKEN_TYPE_VERIFY,
    EMAIL_TOKEN_TYPE_RESET,
)
from app.services.email_service import (
    send_verification_email,
    send_password_reset_email,
)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


async def create_and_send_verification(
    db: AsyncSession, user: User, base_url: str
) -> None:
    raw = _generate_token()
    token_hash = hash_token(raw)
    expires = _now_utc() + timedelta(minutes=settings.VERIFY_EMAIL_EXPIRE_MINUTES)
    row = EmailToken(
        user_id=user.id,
        token_hash=token_hash,
        type=EMAIL_TOKEN_TYPE_VERIFY,
        expires_at=expires,
    )
    db.add(row)
    await db.flush()
    base = str(base_url).rstrip("/")
    link = f"{base}/verify-email?token={raw}"
    await asyncio.to_thread(send_verification_email, user.email, link)


async def verify_email_with_token(db: AsyncSession, raw_token: str) -> User:
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token."
        )
    token_hash = hash_token(raw_token)
    result = await db.execute(
        select(EmailToken).where(
            EmailToken.token_hash == token_hash,
            EmailToken.type == EMAIL_TOKEN_TYPE_VERIFY,
        )
    )
    row = result.scalar_one_or_none()
    if not row or row.used or row.expires_at <= _now_utc():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )
    row.used = True
    user_result = await db.execute(select(User).where(User.id == row.user_id))
    user = user_result.scalar_one()
    user.is_verified = True
    return user


async def create_and_send_password_reset(
    db: AsyncSession, email: str, base_url: str
) -> None:
    from app.services.auth_service import _get_user_by_email

    normalized = email.strip().lower()
    user = await _get_user_by_email(db, normalized)
    if not user:
        return  # Don't leak existence
    raw = _generate_token()
    token_hash = hash_token(raw)
    expires = _now_utc() + timedelta(minutes=settings.RESET_PASSWORD_EXPIRE_MINUTES)
    row = EmailToken(
        user_id=user.id,
        token_hash=token_hash,
        type=EMAIL_TOKEN_TYPE_RESET,
        expires_at=expires,
    )
    db.add(row)
    await db.flush()
    base = str(base_url).rstrip("/")
    link = f"{base}/reset-password?token={raw}"
    await asyncio.to_thread(send_password_reset_email, user.email, link)


async def reset_password_with_token(
    db: AsyncSession, raw_token: str, new_password: str
) -> None:
    from app.core.security import hash_password

    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Missing token."
        )
    token_hash = hash_token(raw_token)
    result = await db.execute(
        select(EmailToken).where(
            EmailToken.token_hash == token_hash,
            EmailToken.type == EMAIL_TOKEN_TYPE_RESET,
        )
    )
    row = result.scalar_one_or_none()
    if not row or row.used or row.expires_at <= _now_utc():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )
    row.used = True
    user_result = await db.execute(select(User).where(User.id == row.user_id))
    user = user_result.scalar_one()
    user.password_hash = hash_password(new_password)
