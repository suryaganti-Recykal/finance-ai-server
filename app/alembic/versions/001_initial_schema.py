"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-01 11:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_companies")),
        sa.UniqueConstraint("email", name=op.f("uq_companies_email")),
        sa.UniqueConstraint("slug", name=op.f("uq_companies_slug")),
    )
    op.create_index("ix_companies_is_active", "companies", ["is_active"])
    op.create_index("ix_companies_slug", "companies", ["slug"])

    op.create_table(
        "departments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("head", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_departments_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_departments")),
    )
    op.create_index("ix_departments_company_id", "departments", ["company_id"])

    op.create_table(
        "users",
        sa.Column("id", sa.String(128), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_users_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index("ix_users_company_id", "users", ["company_id"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    op.create_table(
        "expenses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("department_id", sa.UUID(), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("source_transaction_id", sa.String(255), nullable=True),
        sa.Column("expense_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_duplicate", sa.Boolean(), nullable=False),
        sa.Column("is_anomalous", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_expenses_company_id_companies")),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], name=op.f("fk_expenses_department_id_departments")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_expenses")),
        sa.UniqueConstraint("source_transaction_id", name=op.f("uq_expenses_source_transaction_id")),
    )
    op.create_index("ix_expenses_category", "expenses", ["category"])
    op.create_index("ix_expenses_company_id", "expenses", ["company_id"])
    op.create_index("ix_expenses_expense_date", "expenses", ["expense_date"])
    op.create_index("ix_expenses_is_anomalous", "expenses", ["is_anomalous"])
    op.create_index("ix_expenses_is_duplicate", "expenses", ["is_duplicate"])
    op.create_index("ix_expenses_source", "expenses", ["source"])

    op.create_table(
        "revenues",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("revenue_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_transaction_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_revenues_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_revenues")),
        sa.UniqueConstraint("source_transaction_id", name=op.f("uq_revenues_source_transaction_id")),
    )
    op.create_index("ix_revenues_company_id", "revenues", ["company_id"])
    op.create_index("ix_revenues_revenue_date", "revenues", ["revenue_date"])
    op.create_index("ix_revenues_source", "revenues", ["source"])

    op.create_table(
        "invoices",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("invoice_number", sa.String(100), nullable=False),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("customer_email", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_invoices_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_invoices")),
        sa.UniqueConstraint("invoice_number", name=op.f("uq_invoices_invoice_number")),
    )
    op.create_index("ix_invoices_company_id", "invoices", ["company_id"])
    op.create_index("ix_invoices_due_date", "invoices", ["due_date"])
    op.create_index("ix_invoices_status", "invoices", ["status"])

    op.create_table(
        "collections",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("invoice_id", sa.UUID(), nullable=True),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("payment_method", sa.String(100), nullable=False),
        sa.Column("reference_number", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collection_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_collections_company_id_companies")),
        sa.ForeignKeyConstraint(["invoice_id"], ["invoices.id"], name=op.f("fk_collections_invoice_id_invoices")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_collections")),
    )
    op.create_index("ix_collections_collection_date", "collections", ["collection_date"])
    op.create_index("ix_collections_company_id", "collections", ["company_id"])

    op.create_table(
        "campaigns",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("platform", sa.String(100), nullable=False),
        sa.Column("campaign_id", sa.String(255), nullable=False),
        sa.Column("total_spend", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("leads", sa.Integer(), nullable=False),
        sa.Column("purchases", sa.Integer(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=False),
        sa.Column("clicks", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_campaigns_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaigns")),
        sa.UniqueConstraint("campaign_id", name=op.f("uq_campaigns_campaign_id")),
    )
    op.create_index("ix_campaigns_company_id", "campaigns", ["company_id"])
    op.create_index("ix_campaigns_platform", "campaigns", ["platform"])
    op.create_index("ix_campaigns_status", "campaigns", ["status"])

    op.create_table(
        "budgets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("department_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("budgeted_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("spent_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("fiscal_year", sa.Integer(), nullable=False),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("threshold_80", sa.Boolean(), nullable=False),
        sa.Column("threshold_90", sa.Boolean(), nullable=False),
        sa.Column("threshold_100", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_budgets_company_id_companies")),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], name=op.f("fk_budgets_department_id_departments")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_budgets")),
    )
    op.create_index("ix_budgets_company_id", "budgets", ["company_id"])
    op.create_index("ix_budgets_department_id", "budgets", ["department_id"])

    op.create_table(
        "forecasts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("forecast_type", sa.String(100), nullable=False),
        sa.Column("period", sa.String(50), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("forecasted_value", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("actual_value", sa.Numeric(15, 2), nullable=True),
        sa.Column("variance", sa.Numeric(15, 2), nullable=True),
        sa.Column("confidence_level", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_forecasts_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_forecasts")),
    )
    op.create_index("ix_forecasts_company_id", "forecasts", ["company_id"])
    op.create_index("ix_forecasts_forecast_type", "forecasts", ["forecast_type"])

    op.create_table(
        "reports",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("report_type", sa.String(100), nullable=False),
        sa.Column("period", sa.String(50), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("insights", sa.Text(), nullable=True),
        sa.Column("pdf_file", sa.LargeBinary(), nullable=True),
        sa.Column("excel_file", sa.LargeBinary(), nullable=True),
        sa.Column("generated_by", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_reports_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index("ix_reports_company_id", "reports", ["company_id"])
    op.create_index("ix_reports_report_type", "reports", ["report_type"])

    op.create_table(
        "email_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("report_id", sa.UUID(), nullable=True),
        sa.Column("recipient_email", sa.String(255), nullable=False),
        sa.Column("recipient_role", sa.String(100), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("template", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_email_logs_company_id_companies")),
        sa.ForeignKeyConstraint(["report_id"], ["reports.id"], name=op.f("fk_email_logs_report_id_reports")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_email_logs")),
    )
    op.create_index("ix_email_logs_company_id", "email_logs", ["company_id"])
    op.create_index("ix_email_logs_status", "email_logs", ["status"])

    op.create_table(
        "agent_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("execution_id", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("input_data", sa.Text(), nullable=True),
        sa.Column("output_data", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("execution_time_seconds", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=op.f("fk_agent_logs_company_id_companies")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_agent_logs")),
        sa.UniqueConstraint("execution_id", name=op.f("uq_agent_logs_execution_id")),
    )
    op.create_index("ix_agent_logs_agent_name", "agent_logs", ["agent_name"])
    op.create_index("ix_agent_logs_company_id", "agent_logs", ["company_id"])
    op.create_index("ix_agent_logs_status", "agent_logs", ["status"])


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_logs_status"), table_name="agent_logs")
    op.drop_index(op.f("ix_agent_logs_company_id"), table_name="agent_logs")
    op.drop_index(op.f("ix_agent_logs_agent_name"), table_name="agent_logs")
    op.drop_table("agent_logs")

    op.drop_index(op.f("ix_email_logs_status"), table_name="email_logs")
    op.drop_index(op.f("ix_email_logs_company_id"), table_name="email_logs")
    op.drop_table("email_logs")

    op.drop_index(op.f("ix_reports_report_type"), table_name="reports")
    op.drop_index(op.f("ix_reports_company_id"), table_name="reports")
    op.drop_table("reports")

    op.drop_index(op.f("ix_forecasts_forecast_type"), table_name="forecasts")
    op.drop_index(op.f("ix_forecasts_company_id"), table_name="forecasts")
    op.drop_table("forecasts")

    op.drop_index(op.f("ix_budgets_department_id"), table_name="budgets")
    op.drop_index(op.f("ix_budgets_company_id"), table_name="budgets")
    op.drop_table("budgets")

    op.drop_index(op.f("ix_campaigns_status"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_platform"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_company_id"), table_name="campaigns")
    op.drop_table("campaigns")

    op.drop_index(op.f("ix_collections_company_id"), table_name="collections")
    op.drop_index(op.f("ix_collections_collection_date"), table_name="collections")
    op.drop_table("collections")

    op.drop_index(op.f("ix_invoices_status"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_due_date"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_company_id"), table_name="invoices")
    op.drop_table("invoices")

    op.drop_index(op.f("ix_revenues_source"), table_name="revenues")
    op.drop_index(op.f("ix_revenues_revenue_date"), table_name="revenues")
    op.drop_index(op.f("ix_revenues_company_id"), table_name="revenues")
    op.drop_table("revenues")

    op.drop_index(op.f("ix_expenses_source"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_is_duplicate"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_is_anomalous"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_expense_date"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_company_id"), table_name="expenses")
    op.drop_index(op.f("ix_expenses_category"), table_name="expenses")
    op.drop_table("expenses")

    op.drop_index(op.f("ix_users_is_active"), table_name="users")
    op.drop_index(op.f("ix_users_company_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_departments_company_id"), table_name="departments")
    op.drop_table("departments")

    op.drop_index(op.f("ix_companies_slug"), table_name="companies")
    op.drop_index(op.f("ix_companies_is_active"), table_name="companies")
    op.drop_table("companies")
