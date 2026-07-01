# Marketing Spend Agent

The Marketing Spend Agent automatically calculates marketing KPIs, compares spend against previous periods, and detects anomalies in campaign performance. It integrates data from Meta Ads, Google Ads, and manual campaign entries.

## Key Metrics

### Cost Per Lead (CPL)
How much you spend per lead generated.

**Formula:** `Total Spend / Leads`

**Example:** If you spend $5,000 and get 150 leads, your CPL is $33.33.

### Cost Per Purchase (CPP)
How much you spend per purchase/sale.

**Formula:** `Total Spend / Purchases`

**Example:** If you spend $5,000 and get 25 purchases, your CPP is $200.

### Cost Per Click (CPC)
How much each click costs (ad auction metric).

**Formula:** `Total Spend / Clicks`

**Example:** If you spend $5,000 and get 1,000 clicks, your CPC is $5.00.

### Click-Through Rate (CTR)
Percentage of impressions that resulted in clicks.

**Formula:** `(Clicks / Impressions) * 100`

**Example:** If 50,000 impressions resulted in 1,000 clicks, your CTR is 2%.

### Return On Ad Spend (ROAS)
Revenue generated per dollar spent.

**Formula:** `Revenue from Campaign / Total Spend`

**Note:** Currently a placeholder (requires mapping campaigns to revenue). Will be implemented after revenue tracking is connected.

### Period-over-Period Comparison
Metrics change from the same period last year:
- **Spend Change %:** Current spend vs. last year's spend
- **Leads Change %:** Current leads vs. last year's leads
- **CPL Change %:** Current CPL vs. last year's CPL

## Anomalies Detected

### High Spend Spike
Spend increased >50% vs. previous period.

**Threshold:** 50% increase  
**Severity:** Warning  
**Action:** Review campaign settings, check if intentional budget increase.

### Low Conversion Rate
Very few leads generated relative to clicks.

**Threshold:** <1% click-to-lead conversion  
**Severity:** Warning  
**Action:** Review ad copy, landing page, audience targeting.

### High CPL
Cost per lead exceeded threshold (default: $100).

**Threshold:** $100  
**Severity:** Info  
**Action:** Review audience targeting, landing page quality, ad creative.

**Future:** Will use historical median CPL per campaign/platform instead of fixed threshold.

## API Endpoints

### GET /api/v1/marketing

Get comprehensive marketing report for all campaigns.

**Query parameters:**
- `start_date` (optional): ISO 8601 datetime. Defaults to 30 days ago.
- `end_date` (optional): ISO 8601 datetime. Defaults to now.

**Request:**
```bash
curl -X GET \
  "http://localhost:8000/api/v1/marketing?start_date=2026-06-01T00:00:00Z&end_date=2026-07-01T00:00:00Z" \
  -H "Authorization: Bearer <jwt_token>"
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period_start": "2026-06-01T00:00:00Z",
    "period_end": "2026-07-01T00:00:00Z",
    "total_spend": "25000.00",
    "total_leads": 750,
    "total_purchases": 125,
    "total_impressions": 250000,
    "total_clicks": 5000,
    "overall_cpl": "33.33",
    "overall_cpp": "200.00",
    "overall_ctr": "2.00",
    "campaigns": [
      {
        "campaign_id": "meta_123456",
        "campaign_name": "Summer Sale",
        "platform": "meta",
        "period": "monthly",
        "period_start": "2026-06-01T00:00:00Z",
        "period_end": "2026-07-01T00:00:00Z",
        "total_spend": "5000.00",
        "currency": "USD",
        "leads": 150,
        "purchases": 25,
        "impressions": 50000,
        "clicks": 1000,
        "cpl": "33.33",
        "cpp": "200.00",
        "cpc": "5.00",
        "ctr": "2.00",
        "roas": null,
        "spend_change_percent": "25.00",
        "leads_change_percent": "-10.00",
        "cpl_change_percent": "38.89"
      },
      ...
    ],
    "anomalies": [
      {
        "anomaly_type": "high_spend_spike",
        "severity": "warning",
        "campaign_id": "meta_123456",
        "campaign_name": "Summer Sale",
        "description": "Spend increased by 25.00% vs. previous period",
        "metric_name": "total_spend",
        "expected_value": null,
        "actual_value": "5000.00",
        "threshold": "6250.00",
        "detected_at": "2026-07-01T12:00:00Z"
      },
      {
        "anomaly_type": "low_conversion_rate",
        "severity": "warning",
        "campaign_id": "google_ads_789",
        "campaign_name": "Winter Promo",
        "description": "Only 0.80% click-to-lead conversion",
        "metric_name": "ctr",
        "expected_value": "1.00",
        "actual_value": "0.80",
        "threshold": "1.00",
        "detected_at": "2026-07-01T12:00:00Z"
      }
    ]
  }
}
```

**Errors:**
- `401 Unauthorized`: Missing or invalid JWT
- `400 Bad Request`: Invalid date format

## Dashboard Integration

The Marketing Spend Agent data appears on the main dashboard as:
- **Marketing Spend KPI card** (total across all campaigns)
- **Campaign Spend pie chart** (breakdown by campaign)
- **Marketing Spend trend line** (daily/weekly/monthly)
- **Anomaly alerts** (flagged issues)

## Data Sources

### Meta Ads (Facebook)
Fetched daily by Expense Collection Agent.

**Data points:**
- Campaign name & ID
- Daily spend
- Impressions, clicks, actions (conversions)

### Google Ads
Fetched daily by Expense Collection Agent.

**Data points:**
- Campaign name & ID
- Cost, impressions, clicks
- Conversions

### Manual Campaigns
Entered manually via admin UI or imported from CSV.

**Data points:**
- Campaign details (name, platform, dates)
- Total spend
- Leads, purchases (manual entry or API)

## Scheduling

The Marketing Spend Agent runs:
- **Real-time:** When campaigns data is updated
- **Daily:** As part of the Morning Finance Brief (n8n orchestration)
- **On-demand:** Via API endpoint

## Limitations & Future Work

### Current
- ROAS calculation not implemented (needs revenue mapping)
- Anomaly thresholds are static (plan: ML-based dynamic thresholds)
- Year-over-year comparison assumes same calendar structure
- No cohort analysis (lead quality, repeat purchasers, etc.)

### Planned
- **ML Anomaly Detection:** Train on historical data to detect unexpected patterns
- **Campaign Attribution:** Map leads/purchases to specific campaigns and channels
- **Predictive Spend:** Forecast CPL/CPP trends
- **Competitive Benchmark:** Compare against industry averages
- **Bid Optimization Recommendations:** Suggest platform-specific bid adjustments
- **Budget Allocation:** Recommend spend distribution across campaigns

## Examples

### Example 1: Detecting High CPC

Campaign "Black Friday Sale" shows:
- Spend: $10,000
- Clicks: 500
- CPC: $20 (vs. historical average $5)

**Alert:** High CPC detected. Review bid strategy, landing page quality, audience targeting.

### Example 2: Improving Lead Quality

Comparing two periods:
- **June:** CPL $30, 100 leads
- **July:** CPL $40, 80 leads

**Alert:** CPL increased 33%, leads decreased 20%. Campaign efficiency degrading.

### Example 3: Successful Spend Scale

Campaign "Summer Promo":
- Spend increased 50% ($5k → $7.5k)
- Leads increased 40% (150 → 210)
- CPL improved 7% ($33 → $31)

**Insight:** Higher spend is generating leads at better efficiency. Scale-up successful.

## Security & Privacy

- Campaign data is scoped to authenticated company (multi-tenant)
- Spend metrics are never shown to unauthorized users
- Historical comparisons use previous fiscal period, respecting data retention policies
