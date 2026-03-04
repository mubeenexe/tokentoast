"""
Email sending for verification and password reset.
Uses SMTP when configured; otherwise logs links to console (dev).
"""
from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def _send_smtp(to_email: str, subject: str, body_html: str, body_plain: str) -> None:
    """Send a single email via SMTP. Raises on failure."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email

    msg.attach(MIMEText(body_plain, "plain"))
    msg.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        if settings.SMTP_USE_TLS:
            server.starttls()
        if settings.SMTP_USER and settings.SMTP_PASSWORD:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_FROM_EMAIL, [to_email], msg.as_string())


def send_verification_email(to_email: str, verify_link: str) -> None:
    subject = "Verify your email – TokenToast"
    body_plain = f"Verify your email by opening this link:\n{verify_link}\n\nIf you didn't create an account, ignore this email."
    body_html = f"""
    <p>Verify your email by clicking the link below:</p>
    <p><a href="{verify_link}">Verify email</a></p>
    <p>If you didn't create an account, you can ignore this email.</p>
    """
    if settings.email_enabled:
        try:
            _send_smtp(to_email, subject, body_html.strip(), body_plain)
            logger.info("Verification email sent to %s", to_email)
        except Exception as e:
            logger.exception("Failed to send verification email to %s: %s", to_email, e)
            raise
    else:
        logger.info("[EMAIL] Verification link for %s: %s", to_email, verify_link)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    subject = "Reset your password – TokenToast"
    body_plain = f"Reset your password by opening this link:\n{reset_link}\n\nIf you didn't request this, ignore this email. The link expires in {settings.RESET_PASSWORD_EXPIRE_MINUTES} minutes."
    body_html = f"""
    <p>Reset your password by clicking the link below:</p>
    <p><a href="{reset_link}">Reset password</a></p>
    <p>If you didn't request this, you can ignore this email. The link expires in {settings.RESET_PASSWORD_EXPIRE_MINUTES} minutes.</p>
    """
    if settings.email_enabled:
        try:
            _send_smtp(to_email, subject, body_html.strip(), body_plain)
            logger.info("Password reset email sent to %s", to_email)
        except Exception as e:
            logger.exception("Failed to send password reset email to %s: %s", to_email, e)
            raise
    else:
        logger.info("[EMAIL] Password reset link for %s: %s", to_email, reset_link)
