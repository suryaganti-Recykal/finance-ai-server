# Finance AI Agent - Database Schema

## Core tables

### companies
Multi-tenant root. Every other table references company_id.
- id (UUID, PK)
- name (string)
- email (string, unique)
- slug (string, unique)
- logo_url, website (optional)
- is_active (bool)

### users
Clerk-linked users. Scoped to a company.
- id (string, Clerk user_id, PK)
- company_id (FK → companies)
- email, first_name, last_name
- role (member, admin, finance_lead, etc.)
- is_active (bool)
- created_at

### departments
Organizational units within a company.
- id (UUID, PK)
- company_id (FK → companies)
- name, description, head
- created_at, updated_at

## Financial tables

### expenses
All expenses from any source (Zoho, Meta, Google Ads, Razorpay, bank CSV, credit card).
- id (UUID, PK)
- company_id, department_id (optional)
- amount, currency
- category, description
- source (zoho, meta, google_ads, razorpay, bank, credit_card)
- source_transaction_id (unique per source, prevents duplicates)
- expense_date
- is_duplicate, is_anomalous (flags for AI analysis)
- notes
- created_at, updated_at

### revenues
All revenue/income.
- id (UUID, PK)
- company_id (FK → companies)
- amount, currency
- source, description
- revenue_date
- source_transaction_id (unique)
- created_at, updated_at

### invoices
Invoices sent to customers.
- id (UUID, PK)
- company_id (FK → companies)
- invoice_number (unique)
- customer_name, customer_email
- amount, currency
- status (draft, sent, viewed, paid, overdue, cancelled)
- issue_date, due_date
- description
- created_at, updated_at

### collections
Payments received / collections against invoices.
- id (UUID, PK)
- company_id (FK → companies)
- invoice_id (optional FK → invoices)
- amount, currency
- payment_method (bank_transfer, check, credit_card, etc.)
- reference_number
- collection_date
- created_at, updated_at

## Marketing & Spending

### campaigns
Ad campaigns across platforms (Meta, Google Ads, etc.).
- id (UUID, PK)
- company_id (FK → companies)
- name, platform (meta, google_ads, etc.)
- campaign_id (unique external platform ID)
- total_spend, currency
- leads, purchases, impressions, clicks
- status (active, paused, completed)
- start_date, end_date
- description
- created_at, updated_at

### budgets
Department budgets with threshold tracking.
- id (UUID, PK)
- company_id, department_id (FK)
- name, budgeted_amount, spent_amount, currency
- fiscal_year, quarter (optional)
- threshold_80, threshold_90, threshold_100 (alert flags)
- description
- created_at, updated_at

## Planning & Reporting

### forecasts
AI-generated predictions (revenue, expenses, profit, marketing spend, collections, cash flow).
- id (UUID, PK)
- company_id (FK → companies)
- forecast_type (revenue, expenses, profit, marketing_spend, collections, cash_flow)
- period (monthly, quarterly, yearly)
- period_start, period_end
- forecasted_value, currency
- actual_value (populated once period closes)
- variance (forecasted - actual)
- confidence_level (0-100)
- description
- created_at, updated_at

### reports
Generated reports (PDF, Excel, management summaries).
- id (UUID, PK)
- company_id (FK → companies)
- name, report_type (monthly, quarterly, executive_summary, department_summary)
- period, period_start, period_end
- summary (text)
- insights (AI-generated text)
- pdf_file, excel_file (binary)
- generated_by (agent_name or user)
- created_at

## Logs & Tracking

### email_logs
Email sends.
- id (UUID, PK)
- company_id, report_id (optional FK)
- recipient_email, recipient_role (cfo, finance_team, pod_head, etc.)
- subject, template (template name)
- status (pending, sent, failed)
- sent_at (when actually sent)
- error_message (if failed)
- created_at

### agent_logs
Finance agent executions (expense sync, report generation, forecast update, budget check, etc.).
- id (UUID, PK)
- company_id (FK → companies)
- agent_name (expense_collection, marketing_spend, dashboard, budget_monitoring, monthly_report, email, forecasting, finance_copilot)
- execution_id (unique trace id)
- status (running, completed, failed)
- summary (what was done)
- input_data, output_data (JSON, persisted for debugging)
- error_message (if failed)
- execution_time_seconds
- started_at, completed_at
- created_at (timestamp of log creation)

## Key design patterns

1. **Multi-tenancy**: every table has company_id (row-level, not schema-per-tenant), enforced in repository.
2. **Soft auditing**: created_at, updated_at timestamps on all aggregate roots.
3. **Duplicate & anomaly detection**: is_duplicate, is_anomalous flags on expenses for AI analysis.
4. **External integrations**: source_transaction_id (unique across source type) prevents duplicate imports.
5. **Threshold tracking**: budget thresholds (80%, 90%, 100%) trigger alerts.
6. **JSON fields for flexibility**: input_data, output_data on agent_logs for structured debugging.
7. **Binary storage**: pdf_file, excel_file on reports (could move to S3 later).
8. **Variance tracking**: forecasts compare predicted vs actual once the period closes.

## Indexing strategy

Primary indexes on company_id (tenant filtering), then by:
- expense_date, revenue_date, collection_date (time-range queries)
- category, platform, source (filtering by dimension)
- status (state filtering: draft/sent/paid, active/paused)
- is_duplicate, is_anomalous, agent_name (anomaly/agent-specific queries)
- due_date (overdue invoices)

See migration 001_initial_schema.py for full index definitions.
