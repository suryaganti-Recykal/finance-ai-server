from fastapi import APIRouter

from src.api.v1.routers import auth, budgets, dashboard, expenses, health, marketing

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(budgets.router)
api_router.include_router(dashboard.router)
api_router.include_router(expenses.router)
api_router.include_router(marketing.router)
api_router.include_router(health.router)

# Module routers (expenses, revenue, collections, marketing_spend, budgets,
# forecasting, reports, settings, ai_assistant) attach here one at a time,
# each in the step that builds that module.
