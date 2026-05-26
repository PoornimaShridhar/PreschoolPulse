from datetime import datetime, timezone
from typing import Any

from models.metric_snapshot import MetricSnapshot
from models.recommendation import Recommendation


def _metric_value(metric_snapshot: Any, field_name: str, default: Any) -> Any:
    if isinstance(metric_snapshot, dict):
        return metric_snapshot.get(field_name, default)
    return getattr(metric_snapshot, field_name, default)


def recommend_actions(metric_snapshots: list[Any], monthly_budget: float, target_cost_per_lead: float) -> list[Recommendation]:
    recommendations: list[Recommendation] = []
    spend = sum(float(_metric_value(snapshot, "spend", 0.0)) for snapshot in metric_snapshots)
    budget_ratio = spend / monthly_budget if monthly_budget else 0.0

    for metric_snapshot in metric_snapshots:
        campaign_id = str(_metric_value(metric_snapshot, "campaign_id", "unknown"))
        campaign_name = str(_metric_value(metric_snapshot, "campaign_name", campaign_id))
        cpl = float(_metric_value(metric_snapshot, "cpl", 0.0))
        target_gap = max(0.0, 1.0 - (cpl / target_cost_per_lead)) if target_cost_per_lead else 0.0

        if cpl <= target_cost_per_lead:
            recommendations.append(
                Recommendation(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name,
                    action="Scale",
                    reason=f"Efficient acquisition detected (CPL ${cpl:.2f}).",
                    expected_impact="Increase lead volume without materially raising acquisition cost.",
                    risk="Medium (audience saturation)",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        elif cpl <= target_cost_per_lead * 1.25:
            recommendations.append(
                Recommendation(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name,
                    action="Modify",
                    reason=f"CPL is ${cpl:.2f}, slightly above target.",
                    expected_impact="Improve lead quality and reduce waste before scaling again.",
                    risk="Low (small budget reallocation)",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
        else:
            recommendations.append(
                Recommendation(
                    campaign_id=campaign_id,
                    campaign_name=campaign_name,
                    action="Pause",
                    reason=f"CPL is ${cpl:.2f}, above the ${target_cost_per_lead:.2f} target.",
                    expected_impact="Stop inefficient spend and reallocate budget to better campaigns.",
                    risk="Low (temporary lead volume drop)",
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )

    if budget_ratio < 0.25:
        recommendations.append(
            Recommendation(
                campaign_id="all",
                campaign_name="All campaigns",
                action="Scale",
                reason="Monthly spend is still light for the cycle.",
                expected_impact="Capture more admissions inquiries while maintaining efficient pacing.",
                risk="Low",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )
    elif budget_ratio > 0.75:
        recommendations.append(
            Recommendation(
                campaign_id="all",
                campaign_name="All campaigns",
                action="Modify",
                reason="Most of the monthly budget is already allocated.",
                expected_impact="Reduce overspend risk and avoid audience fatigue.",
                risk="Medium (budget pressure)",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    return recommendations
