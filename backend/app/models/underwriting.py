import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UnderwritingRun(Base):
    __tablename__ = "underwriting_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)
    results: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    application: Mapped["Application"] = relationship(back_populates="underwriting_runs")
    criteria_checks: Mapped[list["CriteriaCheckResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan"
    )


class CriteriaCheckResult(Base):
    __tablename__ = "criteria_check_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("underwriting_runs.id", ondelete="CASCADE"), nullable=False
    )
    # Nullable: SET NULL when a rule is deleted so audit history is preserved
    rule_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("eligibility_rules.id", ondelete="SET NULL")
    )
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lender_programs.id", ondelete="CASCADE"), nullable=False
    )
    lender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lenders.id", ondelete="CASCADE"), nullable=False
    )
    # Denormalized so results survive rule/lender deletion
    rule_type: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text)
    actual_value: Mapped[str | None] = mapped_column(String(255))

    run: Mapped["UnderwritingRun"] = relationship(back_populates="criteria_checks")


# Resolve forward reference
from app.models.application import Application  # noqa: E402, F401
