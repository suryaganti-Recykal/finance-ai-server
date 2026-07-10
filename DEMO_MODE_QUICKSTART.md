# Demo Mode Quick Start

The Finance AI agents are now ready for **presentations and demonstrations** using sample data.

## Start the Server

```bash
cd app
uvicorn src.main:app --reload
```

Server runs at: `http://localhost:8000`

## Access Demo Endpoints

### 1. Get All Demo Data at Once
```bash
curl http://localhost:8000/api/v1/demo/all
```

**Returns:** Expenses, marketing campaigns, budgets, and forecasts in one call.

### 2. Get Specific Demo Data
```bash
# Expenses
curl http://localhost:8000/api/v1/demo/expenses

# Marketing campaigns
curl http://localhost:8000/api/v1/demo/marketing

# Budgets
curl http://localhost:8000/api/v1/demo/budgets

# Forecasts
curl http://localhost:8000/api/v1/demo/forecasts
```

### 3. Run Agents with Demo Data

**Expense Collection Agent:**
```bash
curl -X POST http://localhost:8000/api/v1/expenses/sync \
  -H "x-company-id: demo-company-001"
```

**Dashboard:**
```bash
curl http://localhost:8000/api/v1/dashboard \
  -H "x-company-id: demo-company-001"
```

**Budget Monitoring:**
```bash
curl http://localhost:8000/api/v1/budgets/check \
  -H "x-company-id: demo-company-001"
```

**Marketing Report:**
```bash
curl http://localhost:8000/api/v1/marketing/report \
  -H "x-company-id: demo-company-001"
```

## What's Included in Demo Data

**6 Sample Expenses:**
- Slack subscription ($1,500)
- Google Ads campaign ($2,500)
- AWS hosting ($800)
- Meta Ads ($3,000)
- Office supplies ($450)
- HubSpot CRM ($1,200)

**4 Marketing Campaigns:**
- Winter Sale (Facebook) - 250k impressions, $5,000
- Product Launch (Google Ads) - 450k impressions, $7,500
- Retargeting (Meta) - 150k impressions, $3,000
- Email Newsletter - 25k impressions, $500

**4 Department Budgets:**
- Marketing: $235,000/year
- Operations: $175,000/year
- Engineering: $260,000/year
- Sales: $150,000/year

**3-Month Expense Forecasts**

## API Documentation

All endpoints are documented at:
```
http://localhost:8000/docs
```

Interactive API explorer with try-it-out functionality.

## Integration with Your APIs

When ready to integrate your own data sources:

1. Create new connector in `app/src/infrastructure/connectors/your_api.py`
2. Implement the `Connector` interface
3. Update `app/src/agents/expense_collection_agent/graph.py` to use your connector
4. Set `USE_SHEETS_FOR_DEMO=false` in `.env`

See `SHEETS_INTEGRATION.md` for detailed instructions.

## Presentation Tips

- **No Setup Required:** Demo mode uses built-in sample data, no external APIs needed
- **Fast & Reliable:** All data is generated locally, no network latency
- **Offline Capable:** Works without internet connection
- **Swappable:** Easy to replace demo data with real APIs later
- **Realistic Data:** Sample data simulates real financial scenarios

## Configuration

Demo mode is enabled by default in `app/.env`:
```env
USE_SHEETS_FOR_DEMO=true
```

To disable and use production APIs:
```env
USE_SHEETS_FOR_DEMO=false
```

## Troubleshooting

**Agents not loading demo data?**
- Restart server: `uvicorn src.main:app --reload`
- Confirm `USE_SHEETS_FOR_DEMO=true` in `.env`

**API returning 404?**
- Check server is running on port 8000
- Verify endpoints in `/docs`

**Demo data not appearing?**
- Demo data is built-in, always available
- Check you're calling `/api/v1/demo/*` endpoints

## Next Steps

1. Start the server
2. Visit http://localhost:8000/docs
3. Try the demo endpoints
4. Run the agents against demo data
5. When ready, integrate your real APIs

---

For questions or issues, refer to `SHEETS_INTEGRATION.md` or check the inline code documentation.
