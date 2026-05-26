from typing import Any

from data.sample_data import build_demo_bundle


class MetricsService:
    def __init__(self, database_path) -> None:
        self.database_path = database_path

    def refresh(self) -> dict[str, Any]:
        return self.build_state(build_demo_bundle())

    def build_state(self, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        latest_snapshot = snapshot or build_demo_bundle()
        summary = latest_snapshot.get("summary", {})
        return {
            "snapshot": latest_snapshot,
            "campaigns": latest_snapshot.get("campaigns", []),
            "leads": latest_snapshot.get("leads", []),
            "metric_snapshots": latest_snapshot.get("metric_snapshots", []),
            "recommendations": latest_snapshot.get("recommendations", []),
            "summary": {
                "spend": float(summary.get("spend", 0.0)),
                "leads": int(summary.get("leads", 0)),
                "clicks": int(summary.get("clicks", 0)),
                "impressions": int(summary.get("impressions", 0)),
                "cost_per_lead": float(summary.get("cost_per_lead", 0.0)),
                "click_through_rate": float(summary.get("click_through_rate", 0.0)),
            },
        }
