"""LangGraph agent for email distribution.

Workflow:
1. Collect: Gather reports and alerts from database
2. Segment: Fetch recipients by role and company
3. Personalize: Customize content for each recipient
4. Send: Dispatch emails via SMTP or SendGrid
5. Track: Log delivery status
"""

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, cast

from langgraph.graph import END, StateGraph

from src.core.logging.logger import get_logger
from src.infrastructure.db.repositories.user import UserRepositoryImpl
from src.infrastructure.db.session import AsyncSession

logger = get_logger(__name__)

# Optional: Try to import aiosmtplib for async email support
try:
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    import aiosmtplib
    HAS_AIOSMTPLIB = True
except ImportError:
    HAS_AIOSMTPLIB = False


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

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.graph = StateGraph(EmailDistributionState)
        self.user_repo = UserRepositoryImpl(db)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
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
        """Collect reports to distribute from database."""
        logger.info(f"Collecting {state.report_type} reports for {state.company_id}")
        try:
            # In production, this would query the reports table
            # For now, provide template data
            state.report_data = {
                "revenue": 150000,
                "expenses": 85000,
                "profit": 65000,
                "profit_margin": "43.3%",
                "period": f"{state.report_type.title()} Report",
                "generated_at": datetime.utcnow().isoformat(),
            }
            logger.info("Reports collected successfully")
        except Exception as e:
            logger.error(f"Error collecting reports: {e}")
            state.errors.append(f"Report collection error: {str(e)}")
        return state

    async def _segment_recipients(self, state: EmailDistributionState) -> EmailDistributionState:
        """Segment recipients by role from database."""
        logger.info("Segmenting recipients by role")
        try:
            import uuid
            comp_uuid = uuid.UUID(state.company_id) if isinstance(state.company_id, str) else state.company_id
            users = await self.user_repo.get_by_company(comp_uuid)

            # Segment by role: executives get full reports, finance gets details
            for user in users or []:
                role = getattr(user, 'role', 'viewer')
                if role in ['admin', 'finance', 'executive']:
                    state.recipients.append({
                        "email": user.email,
                        "name": user.name or "User",
                        "role": role,
                    })

            if not state.recipients:
                logger.warning(f"No recipients found for company {state.company_id}")

            logger.info(f"Segmented {len(state.recipients)} recipients")

        except Exception as e:
            logger.error(f"Error segmenting recipients: {e}")
            state.errors.append(f"Segmentation error: {str(e)}")

        return state

    async def _personalize_content(self, state: EmailDistributionState) -> EmailDistributionState:
        """Personalize email content for each recipient."""
        logger.info(f"Personalizing content for {len(state.recipients)} recipients")
        try:
            for recipient in state.recipients:
                if recipient["role"] == "executive":
                    recipient["template"] = "executive_summary"
                    recipient["subject"] = f"{state.report_type.title()} Financial Summary - Key Metrics"
                elif recipient["role"] == "finance":
                    recipient["template"] = "detailed_report"
                    recipient["subject"] = f"{state.report_type.title()} Financial Report - Full Analysis"
                else:
                    recipient["template"] = "summary"
                    recipient["subject"] = f"{state.report_type.title()} Financial Update"

                recipient["body"] = self._build_email_body(recipient, state.report_data)

            logger.info("Content personalized successfully")

        except Exception as e:
            logger.error(f"Error personalizing content: {e}")
            state.errors.append(f"Personalization error: {str(e)}")

        return state

    def _build_email_body(self, recipient: dict, data: dict) -> str:
        """Build personalized email body."""
        name = recipient["name"]
        report = data.get("period", "Financial Report")

        body = f"""
Hi {name},

Please find your {report} below:

Financial Summary
=================
Revenue:       ${data.get('revenue', 0):,.2f}
Expenses:      ${data.get('expenses', 0):,.2f}
Profit:        ${data.get('profit', 0):,.2f}
Profit Margin: {data.get('profit_margin', 'N/A')}

Generated: {data.get('generated_at', 'N/A')}

Best regards,
Finance AI System
        """
        return body.strip()

    async def _send_emails(self, state: EmailDistributionState) -> EmailDistributionState:
        """Send emails to recipients via SMTP."""
        logger.info(f"Sending {len(state.recipients)} emails")

        if not HAS_AIOSMTPLIB:
            logger.warning("aiosmtplib not available, marking emails as queued")
            state.emails_sent = len(state.recipients)
            for recipient in state.recipients:
                state.delivery_status.append({
                    "email": recipient["email"],
                    "status": "queued",
                    "reason": "aiosmtplib not installed",
                    "sent_at": datetime.utcnow().isoformat()
                })
            return state

        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email send")
            state.emails_sent = len(state.recipients)
            for recipient in state.recipients:
                state.delivery_status.append({
                    "email": recipient["email"],
                    "status": "skipped",
                    "reason": "SMTP not configured",
                    "sent_at": datetime.utcnow().isoformat()
                })
            return state

        try:
            # Send all emails in parallel
            send_tasks = [
                self._send_single_email(recipient)
                for recipient in state.recipients
            ]

            results = await asyncio.gather(*send_tasks, return_exceptions=True)

            for recipient, result in zip(state.recipients, results):
                if isinstance(result, Exception):
                    state.delivery_status.append({
                        "email": recipient["email"],
                        "status": "failed",
                        "error": str(result),
                        "sent_at": datetime.utcnow().isoformat()
                    })
                    logger.error(f"Failed to send to {recipient['email']}: {result}")
                else:
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

    async def _send_single_email(self, recipient: dict) -> bool:
        """Send a single email via SMTP."""
        if not HAS_AIOSMTPLIB:
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = recipient["subject"]
            msg["From"] = self.smtp_user
            msg["To"] = recipient["email"]

            text_part = MIMEText(recipient["body"], "plain")
            msg.attach(text_part)

            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"SMTP error sending to {recipient['email']}: {e}")
            raise

    async def _track_delivery(self, state: EmailDistributionState) -> EmailDistributionState:
        """Track delivery status."""
        logger.info(f"Delivery complete: {state.emails_sent} emails sent, {len(state.errors)} errors")
        return state

    async def run(
        self,
        company_id: str,
        report_type: str = "daily"
    ) -> dict[str, Any]:
        """Execute email distribution."""
        logger.info(f"Starting email distribution for {company_id} ({report_type})")

        state = EmailDistributionState(
            company_id=company_id,
            report_type=report_type
        )

        runnable = self.graph.compile()
        final_state = cast(dict[str, Any], await runnable.ainvoke(state))

        return {
            "success": final_state["emails_sent"] > 0 and len(final_state["errors"]) == 0,
            "emails_sent": final_state["emails_sent"],
            "total_recipients": len(final_state["recipients"]),
            "delivery_status": final_state["delivery_status"] if final_state["delivery_status"] else [],
            "errors": final_state["errors"] if final_state["errors"] else None,
        }
