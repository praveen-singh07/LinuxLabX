from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"
    __table_args__ = (
        Index("ix_admin_audit_occurred_at", "occurred_at"),
        Index("ix_admin_audit_action", "action"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    actor_name: Mapped[str] = mapped_column(String(100), nullable=False)
    target_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    target_name: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    previous_value: Mapped[str] = mapped_column(String(80), nullable=False)
    new_value: Mapped[str] = mapped_column(String(80), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
