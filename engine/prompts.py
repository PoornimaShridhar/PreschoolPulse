from __future__ import annotations

from typing import Any


def _metric_value(metric_snapshot: Any, field_name: str, default: Any = "") -> Any:
    if isinstance(metric_snapshot, dict):
        return metric_snapshot.get(field_name, default)
    return getattr(metric_snapshot, field_name, default)


def _recommendation_value(recommendation: Any, field_name: str, default: Any = "") -> Any:
    if isinstance(recommendation, dict):
        return recommendation.get(field_name, default)
    return getattr(recommendation, field_name, default)


def build_coach_prompt(snapshot: dict[str, Any], recommendations: list[Any], model_name: str = "small local model") -> str:
    summary = snapshot.get("summary", {})
    metric_snapshots = snapshot.get("metric_snapshots", [])
    top_recommendations = recommendations[:3]

    metric_lines: list[str] = []
    for metric_snapshot in metric_snapshots:
        metric_lines.append(
            " | ".join(
                [
                    f"campaign_id={_metric_value(metric_snapshot, 'campaign_id', 'unknown')}",
                    f"campaign_name={_metric_value(metric_snapshot, 'campaign_name', 'unknown')}",
                    f"spend=${float(_metric_value(metric_snapshot, 'spend', 0.0)):,.2f}",
                    f"leads={int(_metric_value(metric_snapshot, 'leads', 0))}",
                    f"clicks={int(_metric_value(metric_snapshot, 'clicks', 0))}",
                    f"impressions={int(_metric_value(metric_snapshot, 'impressions', 0))}",
                    f"ctr={float(_metric_value(metric_snapshot, 'ctr', 0.0)):.2f}%",
                    f"cpl=${float(_metric_value(metric_snapshot, 'cpl', 0.0)):,.2f}",
                ]
            )
        )

    recommendation_lines: list[str] = []
    for recommendation in top_recommendations:
        recommendation_lines.append(
            " | ".join(
                [
                    f"campaign={_recommendation_value(recommendation, 'campaign_name', _recommendation_value(recommendation, 'campaign_id', 'unknown'))}",
                    f"action={_recommendation_value(recommendation, 'action', '')}",
                    f"reason={_recommendation_value(recommendation, 'reason', '')}",
                    f"impact={_recommendation_value(recommendation, 'expected_impact', '')}",
                    f"risk={_recommendation_value(recommendation, 'risk', '')}",
                ]
            )
        )

    return f"""You are a cautious ad-optimization coach for a preschool owner.
Use only the campaign data below. Do not invent numbers.
Choose the single best next action and explain it in one short paragraph.
Return valid JSON only with these keys:
- headline
- chosen_campaign
- action
- reason
- expected_impact
- risk
- confidence
- next_step

Model hint: {model_name}

Dashboard summary:
- spend=${float(summary.get('spend', 0.0)):,.2f}
- leads={int(summary.get('leads', 0))}
- clicks={int(summary.get('clicks', 0))}
- impressions={int(summary.get('impressions', 0))}
- cpl=${float(summary.get('cost_per_lead', 0.0)):,.2f}
- ctr={float(summary.get('click_through_rate', 0.0)):.2f}%

Metric snapshots:
{chr(10).join(f'- {line}' for line in metric_lines) if metric_lines else '- none'}

Candidate recommendations:
{chr(10).join(f'- {line}' for line in recommendation_lines) if recommendation_lines else '- none'}

If the data is mixed, prefer the campaign with the lowest CPL and strongest lead volume.
If no recommendation is strong, choose a conservative modify action.
"""
