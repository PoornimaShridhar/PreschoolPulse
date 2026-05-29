from typing import Any

from ads.google_ads import GoogleAdsClient
from engine.llm import build_ai_coach_note
from data.sample_data import build_demo_bundle
from config.settings import AppSettings


class MetricsService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.google_client = GoogleAdsClient(
            developer_token=settings.google_ads_developer_token,
            client_id=settings.google_ads_client_id,
            client_secret=settings.google_ads_client_secret,
            refresh_token=settings.google_ads_refresh_token,
            customer_id=settings.google_ads_customer_id,
            login_customer_id=settings.google_ads_login_customer_id,
        )

    def refresh(self) -> dict[str, Any]:
        snapshot = self.google_client.fetch_metrics()
        return self.build_state(snapshot)

    def build_state(self, snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
        latest_snapshot = snapshot or build_demo_bundle()
        summary = latest_snapshot.get("summary", {})
        recommendations = latest_snapshot.get("recommendations", [])
        state = {
            "snapshot": latest_snapshot,
            "campaigns": latest_snapshot.get("campaigns", []),
            "leads": latest_snapshot.get("leads", []),
            "metric_snapshots": latest_snapshot.get("metric_snapshots", []),
            "recommendations": recommendations,
            "summary": {
                "spend": float(summary.get("spend", 0.0)),
                "leads": int(summary.get("leads", 0)),
                "clicks": int(summary.get("clicks", 0)),
                "impressions": int(summary.get("impressions", 0)),
                "cost_per_lead": float(summary.get("cost_per_lead", 0.0)),
                "click_through_rate": float(summary.get("click_through_rate", 0.0)),
            },
        }
        state["ai_coach_note"] = build_ai_coach_note(latest_snapshot, recommendations, self.settings)
        return state
