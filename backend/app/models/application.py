import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    business: Mapped["Business"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )
    guarantors: Mapped[list["PersonalGuarantor"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    business_credit: Mapped["BusinessCredit"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )
    loan_request: Mapped["LoanRequest"] = relationship(
        back_populates="application", cascade="all, delete-orphan", uselist=False
    )
    underwriting_runs: Mapped[list["UnderwritingRun"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    dba_name: Mapped[str | None] = mapped_column(String(255))
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_email: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_phone: Mapped[str | None] = mapped_column(String(50))
    state: Mapped[str] = mapped_column(String(2), nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    years_in_biz: Mapped[float] = mapped_column(Float, nullable=False)
    naics_code: Mapped[str | None] = mapped_column(String(10))
    annual_revenue: Mapped[float | None] = mapped_column(Float)
    employee_count: Mapped[int | None] = mapped_column(Integer)

    application: Mapped["Application"] = relationship(back_populates="business")


class PersonalGuarantor(Base):
    __tablename__ = "personal_guarantors"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    ssn_last4: Mapped[str | None] = mapped_column(String(4))
    credit_score: Mapped[int | None] = mapped_column(Integer)
    ownership_pct: Mapped[float | None] = mapped_column(Float)

    application: Mapped["Application"] = relationship(back_populates="guarantors")


class BusinessCredit(Base):
    __tablename__ = "business_credits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    fico_sbss: Mapped[int | None] = mapped_column(Integer)
    experian_intelliscore: Mapped[int | None] = mapped_column(Integer)
    duns_paydex: Mapped[int | None] = mapped_column(Integer)
    bankruptcies: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    liens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    judgments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    years_in_file: Mapped[float | None] = mapped_column(Float)

    application: Mapped["Application"] = relationship(back_populates="business_credit")


class LoanRequest(Base):
    __tablename__ = "loan_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    requested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    requested_term_mo: Mapped[int] = mapped_column(Integer, nullable=False)
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    equipment_description: Mapped[str | None] = mapped_column(Text)
    equipment_year: Mapped[int | None] = mapped_column(Integer)
    equipment_age_yrs: Mapped[float | None] = mapped_column(Float)
    equipment_condition: Mapped[str | None] = mapped_column(String(50))
    state_of_operation: Mapped[str | None] = mapped_column(String(2))
    down_payment_pct: Mapped[float | None] = mapped_column(Float)

    application: Mapped["Application"] = relationship(back_populates="loan_request")


# Avoid circular import — UnderwritingRun lives in underwriting.py
from app.models.underwriting import UnderwritingRun  # noqa: E402, F401
