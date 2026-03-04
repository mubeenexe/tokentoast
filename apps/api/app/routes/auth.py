from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
    SessionResponse,
)
from app.services.auth_service import (
    register_user,
    login_user,
    rotate_refresh_token,
    logout_user,
    list_sessions,
    revoke_session_by_id,
)
from app.utils.cookies import (
    set_auth_cookies,
    clear_auth_cookies,
)

from app.utils.rate_limit import (
    rate_limit_login,
    rate_limit_register,
    rate_limit_forgot_password,
)
from app.services.verification_service import (
    create_and_send_verification,
    verify_email_with_token,
    create_and_send_password_reset,
    reset_password_with_token,
)
from app.schemas.auth import (
    VerifyEmailRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    payload: RegisterRequest,
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_register),
):
    user_out, tokens = await register_user(db, payload.email, payload.password)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    await create_and_send_verification(db, user_out, settings.FRONTEND_ORIGIN)
    return user_out


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_login),
):
    user_out, tokens = await login_user(db, payload.email, payload.password)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/logout", response_model=None)
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    await logout_user(db, request.cookies.get("refresh_token"))
    clear_auth_cookies(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/sessions", response_model=list[SessionResponse])
async def get_sessions(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List active sessions (refresh tokens) for the current user."""
    sessions = await list_sessions(
        db, str(current_user.id), request.cookies.get("refresh_token")
    )
    return [SessionResponse(**s) for s in sessions]


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Revoke a specific session (e.g. another device)."""
    await revoke_session_by_id(db, session_id, str(current_user.id))
    return {"message": "Session revoked."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    tokens = await rotate_refresh_token(db, request.cookies.get("refresh_token"))
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return tokens


@router.post("/verify-email")
async def verify_email(
    payload: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await verify_email_with_token(db, payload.token)
    return {"message": "Email verified.", "user": UserResponse.model_validate(user)}


@router.post("/resend-verification")
async def resend_verification(
    request: Request,
    db: AsyncSession = Depends(get_db),
):

    from pydantic import BaseModel

    class Body(BaseModel):
        email: EmailStr

    body = await request.json()
    email = body.get("email")
    if not email:
        raise HTTPException(400, "email required")
    from app.services.auth_service import _get_user_by_email

    user = await _get_user_by_email(db, email.strip().lower())
    if not user or user.is_verified:
        return {
            "message": "If the account exists and is unverified, an email was sent."
        }
    await create_and_send_verification(db, user, settings.FRONTEND_ORIGIN)
    return {"message": "If the account exists and is unverified, an email was sent."}


@router.post("/forgot-password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(rate_limit_forgot_password),
):
    await create_and_send_password_reset(db, payload.email, settings.FRONTEND_ORIGIN)
    return {"message": "If an account exists with that email, a reset link was sent."}


@router.post("/reset-password")
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await reset_password_with_token(db, payload.token, payload.new_password)
    return {"message": "Password has been reset."}


@router.get("/admin/ping")
async def admin_ping(
    current_user: User = Depends(require_roles(["admin"])),
):
    return {"message": "admin ok", "user_id": str(current_user.id)}
