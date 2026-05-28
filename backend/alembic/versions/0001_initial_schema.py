"""initial schema

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lenders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contact_email", sa.String(255)),
        sa.Column("contact_phone", sa.String(50)),
        sa.Column("notes", sa.Text),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "lender_programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "lender_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lenders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("min_amount", sa.Float),
        sa.Column("max_amount", sa.Float),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lender_programs_lender_id", "lender_programs", ["lender_id"])

    op.create_table(
        "eligibility_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lender_programs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule_type", sa.String(100), nullable=False),
        sa.Column("label", sa.String(255)),
        sa.Column("weight", sa.Float, nullable=False, server_default="1.0"),
        sa.Column("parameters", postgresql.JSON, nullable=False, server_default="{}"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_eligibility_rules_program_id", "eligibility_rules", ["program_id"])

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("business_name", sa.String(255), nullable=False),
        sa.Column("dba_name", sa.String(255)),
        sa.Column("owner_name", sa.String(255), nullable=False),
        sa.Column("owner_email", sa.String(255), nullable=False),
        sa.Column("owner_phone", sa.String(50)),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("business_type", sa.String(100), nullable=False),
        sa.Column("years_in_biz", sa.Float, nullable=False),
        sa.Column("naics_code", sa.String(10)),
        sa.Column("annual_revenue", sa.Float),
        sa.Column("employee_count", sa.Integer),
    )

    op.create_table(
        "personal_guarantors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("ssn_last4", sa.String(4)),
        sa.Column("credit_score", sa.Integer),
        sa.Column("ownership_pct", sa.Float),
    )
    op.create_index(
        "ix_personal_guarantors_application_id", "personal_guarantors", ["application_id"]
    )

    op.create_table(
        "business_credits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("fico_sbss", sa.Integer),
        sa.Column("experian_intelliscore", sa.Integer),
        sa.Column("duns_paydex", sa.Integer),
        sa.Column("bankruptcies", sa.Integer, nullable=False, server_default="0"),
        sa.Column("liens", sa.Integer, nullable=False, server_default="0"),
        sa.Column("judgments", sa.Integer, nullable=False, server_default="0"),
        sa.Column("years_in_file", sa.Float),
    )

    op.create_table(
        "loan_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("requested_amount", sa.Float, nullable=False),
        sa.Column("requested_term_mo", sa.Integer, nullable=False),
        sa.Column("equipment_type", sa.String(100), nullable=False),
        sa.Column("equipment_description", sa.Text),
        sa.Column("equipment_year", sa.Integer),
        sa.Column("equipment_age_yrs", sa.Float),
        sa.Column("equipment_condition", sa.String(50)),
        sa.Column("state_of_operation", sa.String(2)),
        sa.Column("down_payment_pct", sa.Float),
    )

    op.create_table(
        "underwriting_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "application_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("applications.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("error_message", sa.Text),
        sa.Column("results", postgresql.JSON),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_underwriting_runs_application_id", "underwriting_runs", ["application_id"]
    )

    op.create_table(
        "criteria_check_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("underwriting_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "rule_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("eligibility_rules.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "program_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lender_programs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "lender_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("lenders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("rule_type", sa.String(100), nullable=False),
        sa.Column("rule_name", sa.String(255), nullable=False),
        sa.Column("weight", sa.Float, nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False),
        sa.Column("reason", sa.Text),
        sa.Column("actual_value", sa.String(255)),
    )
    op.create_index("ix_criteria_check_results_run_id", "criteria_check_results", ["run_id"])


def downgrade() -> None:
    op.drop_table("criteria_check_results")
    op.drop_table("underwriting_runs")
    op.drop_table("loan_requests")
    op.drop_table("business_credits")
    op.drop_table("personal_guarantors")
    op.drop_table("businesses")
    op.drop_table("applications")
    op.drop_table("eligibility_rules")
    op.drop_table("lender_programs")
    op.drop_table("lenders")
