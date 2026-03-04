import uuid
from sqlalchemy import Column, DateTime, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base

EMAIL_TOKEN_TYPE_VERIFY = "verify"
EMAIL_TOKEN_TYPE_RESET = "reset"


class EmailToken(Base):
    __tablename__ = "email_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash = Column(String(255), nullable=False, index=True)
    type = Column(String(20), nullable=False)  # "verify" | "reset"
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
