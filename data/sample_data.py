from dataclasses import asdict
from datetime import datetime, timezone

from engine.rules import recommend_actions
from models.campaign import Campaign
from models.lead import Lead
from models.metric_snapshot import MetricSnapshot


def build_demo_campaigns() -> list[Campaign]:
    return [
        Campaign(campaign_id="camp-open-house", name="Open House Leads", channel="Meta", status="learning"),
        Campaign(campaign_id="camp-enrollment", name="Preschool Enrollment", channel="Google", status="active"),
        Campaign(campaign_id="camp-toddler", name="Toddler Program", channel="Meta", status="active"),
    ]


def build_demo_leads() -> list[Lead]:
    return [
        Lead(
            lead_id="lead-001",
            campaign_id="camp-open-house",
            name="Aanya Sharma",
            stage="new",
            source="Meta",
            contact="aanya@example.com",
            notes="Asked about nursery hours and weekend activity options.",
        ),
        Lead(
            lead_id="lead-002",
            campaign_id="camp-enrollment",
            name="Rahul Mehta",
            stage="contacted",
            source="Google",
            contact="rahul@example.com",
            notes="Requested fee structure and next intake date.",
        ),
        Lead(
            lead_id="lead-003",
            campaign_id="camp-toddler",
            name="Sara Khan",
            stage="toured",
            source="Meta",
            contact="sara@example.com",
            notes="Booked a campus visit for Friday morning.",
        ),
    ]


def build_demo_metric_snapshots() -> list[MetricSnapshot]:
    return [
        MetricSnapshot(
            campaign_id="camp-open-house",
            spend=132.00,
            leads=12,
            clicks=410,
            impressions=15100,
            ctr=2.72,
            cpl=11.00,
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
        MetricSnapshot(
            campaign_id="camp-enrollment",
            spend=358.00,
            leads=10,
            clicks=280,
            impressions=9400,
            ctr=2.98,
            cpl=35.80,
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
        MetricSnapshot(
            campaign_id="camp-toddler",
            spend=290.00,
            leads=4,
            clicks=150,
            impressions=6900,
            ctr=2.17,
            cpl=72.50,
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
    ]


def build_demo_recommendations() -> list[dict]:
    metric_snapshots = build_demo_metric_snapshots()
    return [asdict(recommendation) for recommendation in recommend_actions(metric_snapshots, monthly_budget=1500.0, target_cost_per_lead=35.0)]


def build_demo_bundle() -> dict:
    campaigns = build_demo_campaigns()
    leads = build_demo_leads()
    metric_snapshots = build_demo_metric_snapshots()
    total_spend = round(sum(snapshot.spend for snapshot in metric_snapshots), 2)
    total_leads = sum(snapshot.leads for snapshot in metric_snapshots)
    total_clicks = sum(snapshot.clicks for snapshot in metric_snapshots)
    total_impressions = sum(snapshot.impressions for snapshot in metric_snapshots)
    return {
        "source": "demo",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "budget": 1500.0,
        "summary": {
            "spend": total_spend,
            "leads": total_leads,
            "clicks": total_clicks,
            "impressions": total_impressions,
            "cost_per_lead": round(total_spend / total_leads, 2),
            "click_through_rate": round((total_clicks / total_impressions) * 100, 2),
        },
        "campaigns": [asdict(campaign) for campaign in campaigns],
        "leads": [asdict(lead) for lead in leads],
        "metric_snapshots": [asdict(metric_snapshot) for metric_snapshot in metric_snapshots],
        "recommendations": build_demo_recommendations(),
    }


def build_demo_snapshot() -> dict:
    bundle = build_demo_bundle()
    return {
        "source": bundle["source"],
        "created_at": bundle["created_at"],
        "budget": bundle["budget"],
        "summary": bundle["summary"],
        "campaigns": bundle["campaigns"],
    }


def build_demo_lead_rows() -> list[dict]:
    return [asdict(lead) for lead in build_demo_leads()]


def build_demo_campaign_rows() -> list[dict]:
    return [asdict(campaign) for campaign in build_demo_campaigns()]


def build_demo_metric_snapshot_rows() -> list[dict]:
    return [asdict(metric_snapshot) for metric_snapshot in build_demo_metric_snapshots()]


def build_demo_recommendation_rows() -> list[dict]:
    return build_demo_recommendations()