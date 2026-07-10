from fastapi import APIRouter

from src.api.v1.routers import (
    ai,
    auth,
    budgets,
    dashboard,
    demo,
    expenses,
    forecasts,
    health,
    marketing,
    notifications,
    reports,
    sheets_auth,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(budgets.router)
api_router.include_router(dashboard.router)
api_router.include_router(expenses.router)
api_router.include_router(marketing.router)
api_router.include_router(reports.router)
api_router.include_router(notifications.router)
api_router.include_router(forecasts.router)
api_router.include_router(ai.router)
api_router.include_router(demo.router)
api_router.include_router(sheets_auth.router)
api_router.include_router(health.router)
