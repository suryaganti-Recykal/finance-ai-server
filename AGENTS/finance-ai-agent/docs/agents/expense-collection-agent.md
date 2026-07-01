# Expense Collection Agent

The Expense Collection Agent automatically fetches expenses from 6 integrated sources, deduplicates them, categorizes them, and stores them in the database. It runs daily (scheduled via n8n) and can also be triggered manually.

## Supported sources

### 1. Zoho Books
Fetches all expense transactions from your Zoho Books organization.

**Configuration:**
```env
ZOHO_API_KEY=your_api_key_here
ZOHO_ORG_ID=your_org_id_here
```

**Data points:**
- Transaction ID
- Amount, Currency
- Category (from Zoho)
- Description
- Transaction date
- Merchant/Payee

### 2. Meta Ads (Facebook)
Fetches ad spend and campaign costs from Meta Ads Manager.

**Configuration:**
```env
META_ACCESS_TOKEN=your_access_token
META_AD_ACCOUNT_ID=your_ad_account_id
```

**Data points:**
- Campaign ID
- Amount (daily spend)
- Currency
- Campaign name
- Date
- Status (active/paused)

### 3. Google Ads
Fetches ad spend from Google Ads account.

**Configuration:**
```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_developer_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id
GOOGLE_CUSTOMER_ID=your_google_customer_id
```

**Data points:**
- Campaign ID
- Cost
- Currency
- Campaign name
- Date

### 4. Razorpay
Fetches payment and payout transactions from your Razorpay account.

**Configuration:**
```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

**Data points:**
- Transaction ID
- Amount
- Currency
- Payment method
- Status
- Date

### 5. Bank Statement (CSV)
Upload a CSV export from your bank account.

**Expected format:**
```csv
Date,Description,Amount,Balance,Type
2026-07-01,Office Supplies,500.00,10000.00,Debit
2026-07-02,Salary Deposit,50000.00,60000.00,Credit
```

**Upload:**
```bash
curl -X POST /api/v1/expenses/import-csv \
  -H "Authorization: Bearer <token>" \
  -F "file=@statement.csv" \
  -F "source=bank"
```

### 6. Credit Card Statement (CSV)
Upload a CSV export from your credit card provider.

**Expected format:**
```csv
Date,Merchant,Amount,Category
2026-07-01,AWS,1500.00,Cloud Services
2026-07-02,Starbucks,50.00,Meals
```

**Upload:**
```bash
curl -X POST /api/v1/expenses/import-csv \
  -H "Authorization: Bearer <token>" \
  -F "file=@cc_statement.csv" \
  -F "source=credit_card"
```

## Workflow

```
┌─────────────────────────────────────────┐
│ n8n Scheduler (daily at 2 AM UTC)      │
└──────────┬──────────────────────────────┘
           │ POST /api/v1/expenses/sync
           ▼
┌─────────────────────────────────────────┐
│ Expense Collection Agent                 │
├─────────────────────────────────────────┤
│ 1. Fetch from all sources                │
│    ├─ ZohoConnector.fetch()              │
│    ├─ MetaConnector.fetch()              │
│    ├─ GoogleAdsConnector.fetch()         │
│    ├─ RazorpayConnector.fetch()          │
│    └─ [File upload connectors]           │
├─────────────────────────────────────────┤
│ 2. Deduplicate (by source_transaction_id)│
│    └─ Remove exact duplicates            │
├─────────────────────────────────────────┤
│ 3. Categorize (rule-based)               │
│    ├─ Marketing → facebook, google, ads  │
│    ├─ Operations → aws, server           │
│    ├─ HR → salary, payroll               │
│    └─ etc.                               │
├─────────────────────────────────────────┤
│ 4. Store in database                     │
│    └─ Insert into expenses table         │
└──────┬───────────────────────────────────┘
       │ Returns sync summary
       ▼
   API Response:
   {
     "total_synced": 156,
     "total_duplicates": 3,
     "errors": [],
     "sync_started_at": "2026-07-01T02:00:00Z",
     "sync_completed_at": "2026-07-01T02:03:45Z"
   }
```

## API endpoints

### POST /api/v1/expenses/sync

Manually trigger expense sync from all configured sources.

**Query parameters:**
- `start_date` (optional): ISO 8601 datetime. Defaults to 30 days ago.
- `end_date` (optional): ISO 8601 datetime. Defaults to now.

**Request:**
```bash
curl -X POST \
  "http://localhost:8000/api/v1/expenses/sync" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json"
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_synced": 156,
    "total_duplicates": 3,
    "errors": [],
    "sync_started_at": "2026-07-01T02:00:00Z",
    "sync_completed_at": "2026-07-01T02:03:45Z"
  }
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid JWT
- `401 Unauthorized`: No company_id in token
- `400 Bad Request`: Invalid date format
- `500 Internal Server Error`: Connector or database failure (details in response)

## Deduplication logic

Duplicates are detected by matching `(source, source_transaction_id)`:
- If the same transaction appears twice from the same source, only the first occurrence is stored
- Transactions from different sources (e.g., a Meta spend showing up in Zoho and Meta APIs) are kept as separate records (allowed, as they may have different details)
- Duplicates are counted and reported in the sync summary

## Categorization rules

The agent uses keyword matching to assign categories:

| Category | Keywords |
|----------|----------|
| marketing | facebook, google, meta, ads, adspend |
| operations | aws, server, hosting, infrastructure |
| hr | salary, payroll, employee |
| travel | flight, hotel, taxi, airline |
| meals | restaurant, coffee, food, lunch |
| office | furniture, supplies, desk |
| other | (default for uncategorized) |

**Future enhancement:** Replace with ML-based categorizer trained on historical data.

## Error handling

If a connector fails:
- The sync continues with other sources
- The error is logged and included in the sync response
- Other transactions are still stored
- The sync is not aborted

Example response with errors:
```json
{
  "success": true,
  "data": {
    "total_synced": 120,
    "total_duplicates": 2,
    "errors": [
      "Meta Ads: Authentication failed - check access token",
      "Google Ads: Rate limit exceeded - retry in 60 seconds"
    ],
    "sync_started_at": "2026-07-01T02:00:00Z",
    "sync_completed_at": "2026-07-01T02:05:30Z"
  }
}
```

## Scheduling (n8n)

Create a workflow in n8n:

1. **Trigger**: Schedule (daily at 2 AM UTC)
2. **Node**: HTTP Request
   - Method: `POST`
   - URL: `https://api.yourapp.com/api/v1/expenses/sync`
   - Headers:
     - `Authorization: Bearer <service_token>`
     - `Content-Type: application/json`
3. **Node**: Condition (if sync failed)
   - Send alert to Slack/email on failure

## Security notes

- Connector credentials (API keys, tokens) are stored in `.env` and never logged
- `source_transaction_id` must be unique per source to enable deduplication
- All synced expenses are scoped to the authenticated company (multi-tenant isolation)
- Synced expenses can trigger anomaly detection (flagged with `is_anomalous = true`)

## Future enhancements

- Real-time sync (webhook-based instead of daily batch)
- Incremental sync (only fetch since last sync, not full date range)
- ML-based categorization (train on historical category assignments)
- Anomaly detection (flag unusual amounts, frequencies)
- Duplicate detection across sources (e.g., same transaction in Zoho and Meta)
- Reconciliation (match bank statement to transactions)
- Expense splitting (split invoice across departments)
