"""Aggregates raw marketing spend records into dashboard-ready summaries."""

from collections import defaultdict

from src.infrastructure.connectors.marketing_spend_sheet import BUSINESS_UNITS, SpendRecord


class LiveSpendService:
    """Turns flat SpendRecord rows into chart-friendly aggregates."""

    def summarize(self, records: list[SpendRecord]) -> dict:
        total_spend = sum(r.total for r in records)

        by_team: dict[str, float] = defaultdict(float)
        by_segment: dict[str, float] = defaultdict(float)
        by_type: dict[str, float] = defaultdict(float)
        by_business_unit: dict[str, float] = defaultdict(float)
        by_month: dict[str, float] = defaultdict(float)

        for r in records:
            by_team[r.team] += r.total
            by_segment[r.segment] += r.total
            by_type[r.type] += r.total
            by_month[r.month] += r.total
            for unit in BUSINESS_UNITS:
                by_business_unit[unit] += r.business_units.get(unit, 0.0)

        month_order = [
            "April", "May", "June", "July", "August", "September",
            "October", "November", "December", "January", "February", "March",
        ]
        monthly_trend = [
            {"month": m, "spend": round(by_month.get(m, 0.0), 2)}
            for m in month_order
            if by_month.get(m, 0.0) > 0
        ]

        top_line_items = sorted(
            (
                {
                    "team": r.team,
                    "sub_team": r.sub_team,
                    "segment": r.segment,
                    "type": r.type,
                    "month": r.month,
                    "total": r.total,
                }
                for r in records
            ),
            key=lambda x: x["total"],
            reverse=True,
        )[:10]

        return {
            "total_spend": round(total_spend, 2),
            "record_count": len(records),
            "by_team": [{"name": k, "value": round(v, 2)} for k, v in sorted(by_team.items(), key=lambda x: -x[1])],
            "by_segment": [{"name": k, "value": round(v, 2)} for k, v in sorted(by_segment.items(), key=lambda x: -x[1])],
            "by_type": [{"name": k, "value": round(v, 2)} for k, v in sorted(by_type.items(), key=lambda x: -x[1])],
            "by_business_unit": [{"name": k, "value": round(v, 2)} for k, v in sorted(by_business_unit.items(), key=lambda x: -x[1])],
            "monthly_trend": monthly_trend,
            "top_line_items": top_line_items,
        }
