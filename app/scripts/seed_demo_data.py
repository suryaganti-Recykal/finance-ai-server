import os
import uuid
import random
from datetime import datetime, timedelta, UTC
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.infrastructure.db.models.company import CompanyModel
from src.infrastructure.db.models.user import UserModel
from src.infrastructure.db.models.department import DepartmentModel
from src.infrastructure.db.models.revenue import RevenueModel
from src.infrastructure.db.models.expense import ExpenseModel
from src.infrastructure.db.models.budget import BudgetModel
from src.infrastructure.db.models.campaign import CampaignModel
from src.infrastructure.db.base import Base

# Sync database URL
from src.core.config.settings import get_settings
settings = get_settings()
db_url = settings.DATABASE_URL.replace("sqlite+aiosqlite", "sqlite")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

COMPANY_ID_STR = '550e8400-e29b-41d4-a716-446655440000'
COMPANY_ID = uuid.UUID(COMPANY_ID_STR)

def seed_data():
    Base.metadata.create_all(bind=engine)
    
    with SessionLocal() as session:
        company = session.get(CompanyModel, COMPANY_ID)
        
        if not company:
            company = CompanyModel(
                id=COMPANY_ID,
                name="Recykal",
                email="admin@recykal.com",
                slug="recykal-demo",
                website="https://recykal.com"
            )
            session.add(company)
            
            user = UserModel(
                id="user_123",
                company_id=COMPANY_ID,
                email="admin@recykal.com",
                first_name="Admin",
                last_name="User",
                role="admin"
            )
            session.add(user)

        depts = [
            DepartmentModel(id=uuid.uuid4(), company_id=COMPANY_ID, name="Engineering", head="Alice"),
            DepartmentModel(id=uuid.uuid4(), company_id=COMPANY_ID, name="Sales", head="Bob"),
            DepartmentModel(id=uuid.uuid4(), company_id=COMPANY_ID, name="Marketing", head="Charlie")
        ]
        session.add_all(depts)
        session.flush()

        for dept in depts:
            budget = BudgetModel(
                id=uuid.uuid4(),
                company_id=COMPANY_ID,
                department_id=dept.id,
                name=f"{dept.name} Q3 Budget",
                budgeted_amount=Decimal(random.randint(50000, 150000)),
                spent_amount=Decimal(random.randint(20000, 80000)),
                fiscal_year=2026,
                quarter=3
            )
            session.add(budget)

        campaigns = [
            CampaignModel(
                id=uuid.uuid4(),
                company_id=COMPANY_ID,
                name="Sustainability Drive",
                platform="Google Ads",
                campaign_id="g_123",
                total_spend=Decimal(15000),
                leads=450,
                purchases=120,
                start_date=datetime.now(UTC) - timedelta(days=90)
            ),
            CampaignModel(
                id=uuid.uuid4(),
                company_id=COMPANY_ID,
                name="B2B Recycling Solutions",
                platform="LinkedIn",
                campaign_id="l_456",
                total_spend=Decimal(25000),
                leads=300,
                purchases=85,
                start_date=datetime.now(UTC) - timedelta(days=60)
            )
        ]
        session.add_all(campaigns)

        sources = ["Stripe", "Bank Transfer", "PayPal"]
        categories = ["Software", "Payroll", "Marketing", "Office Supplies", "Travel"]

        for i in range(180):
            date = datetime.now(UTC) - timedelta(days=i)
            
            for _ in range(random.randint(1, 3)):
                rev = RevenueModel(
                    id=uuid.uuid4(),
                    company_id=COMPANY_ID,
                    amount=Decimal(random.uniform(500, 5000)),
                    source=random.choice(sources),
                    revenue_date=date,
                    source_transaction_id=f"rev_{uuid.uuid4().hex[:8]}"
                )
                session.add(rev)

            for _ in range(random.randint(1, 4)):
                exp = ExpenseModel(
                    id=uuid.uuid4(),
                    company_id=COMPANY_ID,
                    department_id=random.choice(depts).id,
                    amount=Decimal(random.uniform(100, 2000)),
                    category=random.choice(categories),
                    source="Corporate Card",
                    expense_date=date,
                    source_transaction_id=f"exp_{uuid.uuid4().hex[:8]}"
                )
                session.add(exp)

        session.commit()
        print("Successfully seeded Recykal demo data (SYNC).")

if __name__ == "__main__":
    seed_data()
