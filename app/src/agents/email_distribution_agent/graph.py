"""LangGraph agent for email distribution.

Workflow:
1. Collect: Gather reports and alerts
2. Segment: Determine recipients by role
3. Personalize: Customize content for each recipient
4. Send: Dispatch emails
5. Track: Log delivery status
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from langgraph.graph import StateGraph, END

from src.core.logging.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EmailDistributionState:
    """State for email distribution."""
    company_id: str
    report_type: str  # "daily", "weekly", "monthly"
    recipients: list[dict] = field(default_factory=list)
    report_data: dict = field(default_factory=dict)
    emails_sent: int = 0
    delivery_status: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class EmailDistributionGraph:
    """LangGraph implementation of email distribution."""

    def __init__(self) -> None:
        self.graph = StateGraph(EmailDistributionState)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph workflow."""
        self.graph.add_node("collect", self._collect_reports)
        self.graph.add_node("segment", self._segment_recipients)
        self.graph.add_node("personalize", self._personalize_content)
        self.graph.add_node("send", self._send_emails)
        self.graph.add_node("track", self._track_delivery)

        self.graph.set_entry_point("collect")
        self.graph.add_edge("collect", "segment")
        self.graph.add_edge("segment", "personalize")
        self.graph.add_edge("personalize", "send")
        self.graph.add_edge("send", "track")
        self.graph.add_edge("track", END)

    async def _collect_reports(self, state: EmailDistributionState) -> EmailDistributionState:
        """Collect reports to distribute."""
        logger.info(f"Collecting {state.report_type} reports")
        state.report_data = {
            "revenue": 150000,
            "expenses": 85000,
            "profit": 65000,
            "profit_margin": "43.3%",
        }
        return state

    async def _segment_recipients(self, state: EmailDistributionState) -> EmailDistributionState:
        """Segment recipients by role."""
        logger.info("Segmenting recipients")
        state.recipients = [
            {"email": "cfo@company.com", "name": "CFO", "role": "finance"},
            {"email": "ceo@company.com", "name": "CEO", "role": "executive"},
            {"email": "accounting@company.com", "name": "Accounting", "role": "finance"},
        ]
        return state

    async def _personalize_content(self, state: EmailDistributionState) -> EmailDistributionState:
        """Personalize email content."""
        logger.info(f"Personalizing content for {len(state.recipients)} recipients")
        for recipient in state.recipients:
            recipient["subject"] = f"{state.report_type.title()} Financial Report"
            recipient["template"] = f"financial_report_{recipient['role']}"
        return state

    async def _send_emails(self, state: EmailDistributionState) -> EmailDistributionState:
        """Send emails to recipients."""
        logger.info(f"Sending {len(state.recipients)} emails")
        try:
            for recipient in state.recipients:
                # Simulate email sending (in production, use SendGrid, AWS SES, etc.)
                state.emails_sent += 1
                state.delivery_status.append({
                    "email": recipient["email"],
                    "status": "sent",
                    "sent_at": datetime.utcnow().isoformat()
                })
                logger.info(f"Email sent to {recipient['email']}")
        except Exception as e:
            logger.error(f"Error sending emails: {e}")
            state.errors.append(f"Email send error: {str(e)}")
        return state

    async def _track_delivery(self, state: EmailDistributionState) -> EmailDistributionState:
        """Track delivery status."""
        logger.info(f"Delivery complete: {state.emails_sent} emails sent")
        return state

    async def run(
        self,
        company_id: str,
        report_type: str = "daily",
        recipients: list[str] | None = None
    ) -> dict[str, Any]:
        """Execute email distribution."""
        logger.info(f"Starting email distribution for {company_id}")

        state = EmailDistributionState(
            company_id=company_id,
            report_type=report_type
        )

        runnable = self.graph.compile()
        final_state = await runnable.ainvoke(state)

        return {
            "success": final_state.emails_sent > 0,
            "emails_sent": final_state.emails_sent,
            "delivery_status": final_state.delivery_status,
            "errors": final_state.errors if final_state.errors else None,
        }
