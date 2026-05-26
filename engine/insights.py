from typing import Any


def _recommendation_value(recommendation: Any, field_name: str, default: Any) -> Any:
    if isinstance(recommendation, dict):
        return recommendation.get(field_name, default)
    return getattr(recommendation, field_name, default)


def build_insight_text(snapshot: dict[str, Any], recommendations: list[Any]) -> str:
    summary = snapshot.get("summary", {})
    spend = float(summary.get("spend", 0.0))
    leads = int(summary.get("leads", 0))
    cost_per_lead = float(summary.get("cost_per_lead", 0.0))
    ctr = float(summary.get("click_through_rate", 0.0))

    lines = [
        f"Tracked spend: ${spend:.2f}",
        f"Leads captured: {leads}",
        f"Cost per lead: ${cost_per_lead:.2f}",
        f"Click-through rate: {ctr:.2f}%",
        "",
        "Recommended next moves:",
    ]
    lines.extend(
        f"- {_recommendation_value(recommendation, 'campaign_name', _recommendation_value(recommendation, 'campaign_id', 'unknown'))}: Recommended action: {_recommendation_value(recommendation, 'action', 'Modify')} | Reason: {_recommendation_value(recommendation, 'reason', '')} | Risk: {_recommendation_value(recommendation, 'risk', 'Low')}"
        for recommendation in recommendations
    )
    return "\n".join(lines)
