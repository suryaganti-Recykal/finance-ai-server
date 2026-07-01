"""LangGraph agent for generating monthly financial reports.

Workflow:
1. Aggregate: Collect all monthly financial data
2. Analyze: Calculate performance metrics and insights
3. Generate: Create PDF/Excel report
4. Summarize: Generate AI insights
5. Store: Save report to database
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MonthlyReportState:
    """State for monthly report generation."""
    company_id: str
    year: int
    month: int

    # Financial data
    total_revenue: Decimal = Decimal(0)
    total_expenses: Decimal = Decimal(0)
    total_profit: Decimal = Decimal(0)
    total_collections: Decimal = Decimal(0)

    # Department breakdown
    departments: list[dict] = field(default_factory=list)

    # Performance metrics
    profit_margin: Decimal = Decimal(0)
    growth_vs_previous: Decimal = Decimal(0)
    cash_position: Decimal = Decimal(0)

    # AI insights
    insights: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Report output
    report_title: str = ""
    report_content: str = ""
    report_format: str = "pdf"  # pdf or excel

    # Tracking
    generated_at: datetime = field(default_factory=datetime.utcnow)
    errors: list[str] = field(default_factory=list)


class MonthlyReportGraph:
    """LangGraph implementation of monthly report generation."""

    def __init__(self) -> None:
        self.graph = StateGraph(MonthlyReportState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("aggregate", self._aggregate_data)
        self.graph.add_node("analyze", self._analyze_metrics)
        self.graph.add_node("generate_insights", self._generate_insights)
        self.graph.add_node("create_report", self._create_report)
        self.graph.add_node("store", self._store_report)

        self.graph.set_entry_point("aggregate")
        self.graph.add_edge("aggregate", "analyze")
        self.graph.add_edge("analyze", "generate_insights")
        self.graph.add_edge("generate_insights", "create_report")
        self.graph.add_edge("create_report", "store")
        self.graph.add_edge("store", END)

    async def _aggregate_data(self, state: MonthlyReportState) -> MonthlyReportState:
        """Aggregate monthly financial data."""
        logger.info(f"Aggregating data for {state.year}-{state.month:02d}")

        try:
            # Simulate data aggregation
            state.total_revenue = Decimal("150000")
            state.total_expenses = Decimal("85000")
            state.total_profit = state.total_revenue - state.total_expenses
            state.total_collections = Decimal("120000")
            state.cash_position = Decimal("250000")

            # Department breakdown
            state.departments = [
                {"name": "Marketing", "spend": 15000, "roi": 5.2},
                {"name": "Operations", "spend": 35000, "roi": 1.8},
                {"name": "HR", "spend": 20000, "roi": 1.5},
                {"name": "Sales", "spend": 15000, "roi": 3.2},
            ]

            logger.info("Data aggregated successfully")

        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            state.errors.append(f"Aggregation error: {str(e)}")

        return state

    async def _analyze_metrics(self, state: MonthlyReportState) -> MonthlyReportState:
        """Analyze financial metrics."""
        logger.info("Analyzing financial metrics")

        try:
            if state.total_revenue > 0:
                state.profit_margin = (state.total_profit / state.total_revenue * 100)
            else:
                state.profit_margin = Decimal(0)

            # Simulate growth calculation (vs previous month)
            state.growth_vs_previous = Decimal("8.5")  # 8.5% growth

            logger.info(f"Profit Margin: {state.profit_margin}%, Growth: {state.growth_vs_previous}%")

        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
            state.errors.append(f"Analysis error: {str(e)}")

        return state

    async def _generate_insights(self, state: MonthlyReportState) -> MonthlyReportState:
        """Generate AI-powered insights."""
        logger.info("Generating AI insights")

        try:
            # Simulate AI insights (in production, use Claude/OpenAI API)
            state.insights = [
                "Revenue increased 8.5% month-over-month, driven by strong sales performance",
                "Profit margin improved to 43% due to operational efficiency gains",
                "Marketing ROI of 5.2x exceeds target of 4.0x",
                "Cash position remains strong at $250k, providing runway for 3+ months",
            ]

            state.recommendations = [
                "Continue marketing momentum - consider increasing budget by 10%",
                "Optimize operations to maintain current efficiency levels",
                "Monitor cash burn rate to ensure runway extends beyond 6 months",
                "Review HR budget allocation - efficiency gains possible",
            ]

            logger.info(f"Generated {len(state.insights)} insights and {len(state.recommendations)} recommendations")

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            state.errors.append(f"Insight generation error: {str(e)}")

        return state

    async def _create_report(self, state: MonthlyReportState) -> MonthlyReportState:
        """Create PDF/Excel report."""
        logger.info("Creating report document")

        try:
            state.report_title = f"Financial Report - {state.year}-{state.month:02d}"

            # Simulate report content generation
            state.report_content = f"""
MONTHLY FINANCIAL REPORT
{state.year}-{state.month:02d}

EXECUTIVE SUMMARY
================
Revenue:              ${state.total_revenue:,.2f}
Expenses:             ${state.total_expenses:,.2f}
Profit:               ${state.total_profit:,.2f}
Profit Margin:        {state.profit_margin:.1f}%
Growth vs Prior:      {state.growth_vs_previous:.1f}%
Cash Position:        ${state.cash_position:,.2f}

KEY INSIGHTS
============
{chr(10).join(f"• {insight}" for insight in state.insights)}

RECOMMENDATIONS
===============
{chr(10).join(f"• {rec}" for rec in state.recommendations)}

DEPARTMENT BREAKDOWN
====================
{chr(10).join(f"{dept['name']}: ${dept['spend']:,.0f} (ROI: {dept['roi']}x)" for dept in state.departments)}
            """

            logger.info("Report created successfully")

        except Exception as e:
            logger.error(f"Error creating report: {e}")
            state.errors.append(f"Report creation error: {str(e)}")

        return state

    async def _store_report(self, state: MonthlyReportState) -> MonthlyReportState:
        """Store report in database."""
        logger.info("Storing report in database")

        try:
            # In production, save to database with PDF/Excel binary
            logger.info(f"Report stored: {state.report_title}")

        except Exception as e:
            logger.error(f"Error storing report: {e}")
            state.errors.append(f"Storage error: {str(e)}")

        return state

    async def run(
        self,
        company_id: str,
        year: int,
        month: int,
        report_format: str = "pdf"
    ) -> dict[str, Any]:
        """Execute monthly report generation."""
        logger.info(f"Starting monthly report for {company_id} ({year}-{month:02d})")

        state = MonthlyReportState(
            company_id=company_id,
            year=year,
            month=month,
            report_format=report_format
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": len(final_state.errors) == 0,
            "report_title": final_state.report_title,
            "summary": {
                "revenue": float(final_state.total_revenue),
                "expenses": float(final_state.total_expenses),
                "profit": float(final_state.total_profit),
                "profit_margin_percent": float(final_state.profit_margin),
                "growth_percent": float(final_state.growth_vs_previous),
                "cash_position": float(final_state.cash_position),
            },
            "insights": final_state.insights,
            "recommendations": final_state.recommendations,
            "departments": final_state.departments,
            "report_format": final_state.report_format,
            "generated_at": final_state.generated_at.isoformat(),
            "errors": final_state.errors if final_state.errors else None,
        }
