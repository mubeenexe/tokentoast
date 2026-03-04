"""
Security event logging for auth-related events (e.g. refresh token reuse).
Use structured logs so they can be shipped to a SIEM or monitored.
"""
import logging

security_logger = logging.getLogger("app.security")


def log_refresh_token_reuse(user_id: str) -> None:
    """Call when a revoked refresh token is presented (reuse attack)."""
    security_logger.warning(
        "Refresh token reuse detected; all sessions revoked",
        extra={"event": "refresh_token_reuse", "user_id": str(user_id)},
    )
