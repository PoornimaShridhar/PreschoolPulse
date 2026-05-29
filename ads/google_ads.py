from typing import Any

from data.sample_data import build_demo_bundle, build_demo_snapshot
from engine.rules import recommend_actions


def _metric_rows_from_campaigns(campaigns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for campaign in campaigns:
        rows.append(
            {
                "campaign_id": campaign.get("campaign_id", ""),
                "spend": float(campaign.get("spend", 0.0)),
                "leads": int(campaign.get("leads", 0)),
                "clicks": int(campaign.get("clicks", 0)),
                "impressions": int(campaign.get("impressions", 0)),
                "ctr": float(campaign.get("ctr", 0.0)),
                "cpl": float(campaign.get("cpl", 0.0)),
            }
        )
    return rows


def _campaign_rows_from_snapshot(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    campaigns = snapshot.get("campaigns", [])
    metric_snapshots = {str(metric["campaign_id"]): metric for metric in snapshot.get("metric_snapshots", [])}
    rows: list[dict[str, Any]] = []
    for campaign in campaigns:
        metric = metric_snapshots.get(str(campaign.get("campaign_id", "")), {})
        rows.append(
            {
                **campaign,
                "spend": float(metric.get("spend", 0.0)),
                "leads": int(metric.get("leads", 0)),
                "clicks": int(metric.get("clicks", 0)),
                "impressions": int(metric.get("impressions", 0)),
                "ctr": float(metric.get("ctr", 0.0)),
                "cpl": float(metric.get("cpl", 0.0)),
            }
        )
    return rows


class GoogleAdsClient:
    def __init__(self, developer_token: str = "", client_id: str = "", client_secret: str = "", refresh_token: str = "", customer_id: str = "", login_customer_id: str = "") -> None:
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.customer_id = customer_id
        self.login_customer_id = login_customer_id

    def fetch_metrics(self) -> dict:
        try:
            from google.ads.googleads.client import GoogleAdsClient as GoogleAdsSdkClient

            if not all([self.developer_token, self.client_id, self.client_secret, self.refresh_token, self.customer_id]):
                raise ValueError("Missing Google Ads credentials")

            config = {
                "developer_token": self.developer_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
                "use_proto_plus": True,
            }
            if self.login_customer_id:
                config["login_customer_id"] = self.login_customer_id

            client = GoogleAdsSdkClient.load_from_dict(config)
            ga_service = client.get_service("GoogleAdsService")
            query = """
                SELECT
                  campaign.id,
                  campaign.name,
                  campaign.status,
                  metrics.cost_micros,
                  metrics.clicks,
                  metrics.impressions,
                  metrics.ctr,
                  metrics.conversions
                FROM campaign
                WHERE campaign.status != 'REMOVED'
            """
            response = ga_service.search(customer_id=self.customer_id, query=query)
            campaigns: list[dict[str, Any]] = []
            for row in response:
                campaign = row.campaign
                metrics = row.metrics
                spend = float(metrics.cost_micros) / 1_000_000 if metrics.cost_micros else 0.0
                leads = int(metrics.conversions) if metrics.conversions else 0
                cpl = round(spend / leads, 2) if leads else 0.0
                campaigns.append(
                    {
                        "campaign_id": str(campaign.id),
                        "name": campaign.name,
                        "channel": "Google",
                        "status": str(campaign.status).split(".")[-1].lower(),
                        "spend": round(spend, 2),
                        "leads": leads,
                        "clicks": int(metrics.clicks or 0),
                        "impressions": int(metrics.impressions or 0),
                        "ctr": float(metrics.ctr or 0.0),
                        "cpl": cpl,
                    }
                )

            snapshot = build_demo_snapshot()
            if campaigns:
                snapshot["source"] = "google-live"
                snapshot["campaigns"] = campaigns
                snapshot["summary"]["spend"] = round(sum(item["spend"] for item in campaigns), 2)
                snapshot["summary"]["leads"] = sum(item["leads"] for item in campaigns)
                snapshot["summary"]["clicks"] = sum(item["clicks"] for item in campaigns)
                snapshot["summary"]["impressions"] = sum(item["impressions"] for item in campaigns)
                snapshot["summary"]["cost_per_lead"] = round(snapshot["summary"]["spend"] / snapshot["summary"]["leads"], 2) if snapshot["summary"]["leads"] else 0.0
                snapshot["summary"]["click_through_rate"] = round((snapshot["summary"]["clicks"] / snapshot["summary"]["impressions"]) * 100, 2) if snapshot["summary"]["impressions"] else 0.0
                snapshot["metric_snapshots"] = _metric_rows_from_campaigns(campaigns)
                snapshot["recommendations"] = [
                    recommendation.__dict__
                    for recommendation in recommend_actions(snapshot["metric_snapshots"], monthly_budget=1500.0, target_cost_per_lead=35.0)
                ]
            return snapshot
        except Exception:
            snapshot = build_demo_snapshot()
            snapshot["source"] = "google-demo"
            return snapshot
