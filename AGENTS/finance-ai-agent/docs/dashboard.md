# Dashboard

The executive dashboard provides real-time KPIs, trends, and breakdowns of the company's financial state. All metrics are calculated from the underlying expense, revenue, invoice, and campaign data.

## KPI Cards (summary)

### Revenue
Total income for the period.

**Formula:** `SUM(revenues.amount WHERE revenue_date IN [start_date, end_date])`

### Expenses
Total spending (all categories: Zoho, Meta, Google Ads, Razorpay, bank, credit card).

**Formula:** `SUM(expenses.amount WHERE expense_date IN [start_date, end_date])`

### Profit
Gross profit for the period.

**Formula:** `Revenue - Expenses`

### Collections
Actual cash received from customers (from invoices).

**Formula:** `SUM(collections.amount WHERE collection_date IN [start_date, end_date])`

### Cash Balance
Current cash on hand (from a linked bank account or manual entry) + Collections in period.

**Formula:** `cash_account_balance + Collections`

**Note:** Cash balance currently returns 0 (placeholder for bank integration).

### Outstanding Receivables
Total value of unpaid invoices.

**Formula:** `SUM(invoices.amount WHERE status IN ['sent', 'viewed', 'overdue'])`

### Marketing Spend
Total ad spend across all platforms (Meta, Google Ads, etc.).

**Formula:** `SUM(campaigns.total_spend WHERE start_date IN [start_date, end_date])`

### Runway (Cash Runway)
Estimated days of operations at current burn rate.

**Formula:**
```
burn_rate = Expenses / period_days
cash_available = Cash Balance - Outstanding Payables
runway_days = cash_available / burn_rate
```

Returns 999 if burn_rate ≤ 0 (no spending).

## Charts

### Revenue Trend (line chart)
Daily revenue over the period. Helps identify seasonal patterns, growth/decline.

**Query:** `SELECT date(revenue_date), SUM(amount) FROM revenues GROUP BY date(revenue_date) ORDER BY date`

### Expense Trend (line chart)
Daily expenses over the period.

**Query:** `SELECT date(expense_date), SUM(amount) FROM expenses GROUP BY date(expense_date) ORDER BY date`

### Collections Trend (line chart)
Daily cash received over the period. Lag between invoicing (revenue) and collection (cash) is visible here.

**Query:** `SELECT date(collection_date), SUM(amount) FROM collections GROUP BY date(collection_date) ORDER BY date`

### Department Spend (pie chart)
Spending broken down by department (HR, Marketing, Operations, Sales, Tech).

**Query:**
```sql
SELECT departments.name, SUM(expenses.amount)
FROM expenses
JOIN departments ON expenses.department_id = departments.id
WHERE expense_date IN [start_date, end_date]
GROUP BY departments.id
```

### Budget Utilization (pie chart)
Budgeted vs. spent for each department (current fiscal year).

**Query:**
```sql
SELECT departments.name, budgets.budgeted_amount, budgets.spent_amount
FROM budgets
JOIN departments ON budgets.department_id = departments.id
WHERE fiscal_year = YEAR(NOW())
```

## Breakdowns

### Campaign Spend
Marketing campaigns with ROAS, CAC, cost per lead.

**Columns:**
- Campaign Name
- Platform (Meta, Google Ads, etc.)
- Total Spend
- Leads Generated
- Purchases
- Cost Per Lead (CPL) = `Spend / Leads`
- Cost Per Purchase (CPP) = `Spend / Purchases`

**Query:** `SELECT campaigns.* WHERE start_date IN [start_date, end_date]`

## Endpoints

### GET /api/v1/dashboard

**Query params:**
- `start_date` (optional): ISO 8601 datetime. Defaults to 30 days ago.
- `end_date` (optional): ISO 8601 datetime. Defaults to now.

**Response:**
```json
{
  "success": true,
  "data": {
    "period_start": "2026-06-01T00:00:00Z",
    "period_end": "2026-07-01T00:00:00Z",
    "kpis": {
      "revenue": {
        "label": "Revenue",
        "value": "100000.00",
        "currency": "USD",
        "change_percent": null,
        "change_direction": null
      },
      "expenses": { ... },
      "profit": { ... },
      "collections": { ... },
      "cash_balance": { ... },
      "outstanding_receivables": { ... },
      "marketing_spend": { ... },
      "runway": { ... }
    }
  }
}
```

### GET /api/v1/dashboard/trends

**Query params:**
- `start_date`, `end_date` (optional): Defaults to 90 days.

**Response:**
```json
{
  "success": true,
  "data": {
    "revenue_trend": {
      "label": "Revenue",
      "currency": "USD",
      "data": [
        { "date": "2026-06-01", "value": "5000.00" },
        { "date": "2026-06-02", "value": "7500.00" },
        ...
      ]
    },
    "expense_trend": { ... },
    "collections_trend": { ... }
  }
}
```

### GET /api/v1/dashboard/department-spend

**Response:**
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "department_name": "Marketing",
        "amount": "25000.00",
        "percentage": "25.0"
      },
      ...
    ]
  }
}
```

### GET /api/v1/dashboard/budget-utilization

**Response:**
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "department_name": "Marketing",
        "budgeted": "50000.00",
        "spent": "40000.00",
        "utilization_percent": "80.0"
      },
      ...
    ]
  }
}
```

### GET /api/v1/dashboard/campaigns

**Query params:**
- `start_date`, `end_date` (optional): Defaults to 30 days.

**Response:**
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "name": "Summer Sale 2026",
        "platform": "meta",
        "spend": "5000.00",
        "leads": 150,
        "purchases": 25,
        "cpl": "33.33",
        "cpc": "200.00"
      },
      ...
    ]
  }
}
```

## Calculation notes

- **No timezone conversion**: All timestamps are assumed UTC. Frontend should handle timezone display.
- **Partial periods**: If `start_date` is mid-month, the KPIs reflect partial-month totals.
- **Real-time**: Dashboard queries run at request time (no caching). For high-traffic deployments, consider caching or materialized views.
- **Null handling**: Missing values default to 0 (e.g., no collections → 0, no campaigns → empty list).
- **Decimal precision**: All currency values are `Decimal(15, 2)` (PostgreSQL NUMERIC).

## Future enhancements

- Year-over-year growth % on KPI cards
- Forecast vs. actual variance (once forecasts are populated)
- Anomaly detection (flag unusual spend spikes)
- Custom date range presets (This Month, Last Quarter, YTD)
- Drill-down from pie chart to transaction list
- Automated alerts (budget threshold, overdue invoices)
