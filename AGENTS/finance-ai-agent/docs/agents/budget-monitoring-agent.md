# Budget Monitoring Agent

The Budget Monitoring Agent tracks department spending against budgets and automatically alerts when thresholds (80%, 90%, 100%) are exceeded. It runs daily as part of the Morning Finance Brief.

## Thresholds & Alerts

| Utilization | Level | Alert Type | Action |
|-------------|-------|-----------|--------|
| 0–79% | Normal | None | Monitor |
| 80%+ | Warning | Yellow | Review spending |
| 90%+ | Critical | Orange | Escalate to head |
| 100%+ | Overbudget | Red | Stop discretionary spending |

## KPIs Tracked

- **Utilization %:** `(Spent / Budgeted) × 100`
- **Remaining Amount:** `Budgeted - Spent`
- **Spending Pace:** Days left × daily burn rate

## API Endpoint

### GET /api/v1/budgets

Get budget status and active alerts for a fiscal period.

**Query params:**
- `fiscal_year` (required): e.g., 2026
- `quarter` (optional): 1–4

**Response:**
```json
{
  "success": true,
  "data": {
    "fiscal_year": 2026,
    "quarter": 2,
    "total_budgeted": "500000.00",
    "total_spent": "375000.00",
    "overall_utilization_percent": "75.00",
    "budgets": [
      {
        "budget_id": "uuid",
        "department_name": "Marketing",
        "budgeted_amount": "100000.00",
        "spent_amount": "92000.00",
        "remaining_amount": "8000.00",
        "utilization_percent": "92.00",
        "threshold_80_triggered": true,
        "threshold_90_triggered": true,
        "threshold_100_triggered": false
      },
      ...
    ],
    "active_alerts": [
      {
        "alert_id": "uuid",
        "department_name": "Marketing",
        "threshold_percent": 90,
        "utilization_percent": "92.00",
        "alert_level": "critical",
        "triggered_at": "2026-07-01T10:30:00Z"
      },
      ...
    ]
  }
}
```

## Alert Workflow

```
Daily (9 AM UTC)
  ↓
Check all budgets
  ├─ Sum expenses by department (YTD)
  ├─ Calculate utilization %
  └─ Compare to thresholds (80%, 90%, 100%)
  ↓
If threshold crossed
  ├─ Create alert
  ├─ Mark threshold flag in DB
  └─ Include in daily digest
  ↓
Email Agent picks up alerts
  └─ Sends to department head & finance
```

## Future Enhancements

- Predictive alert (ETA to 100% based on burn rate)
- Budget reallocation API (move funds between departments)
- Spending approval workflow
- Trend analysis (on track, ahead of pace, behind)
- Multi-level alerts (50%, 75%, escalation logic)
