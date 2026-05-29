from typing import Any

import gradio as gr

from config.settings import AppSettings
from engine.insights import build_insight_text
from engine.rules import recommend_actions
from services.metrics import MetricsService


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _build_metrics_cards(summary: dict[str, Any]) -> str:
    cards = [
        ("Spend", _format_currency(summary.get("spend", 0.0))),
        ("Leads", str(summary.get("leads", 0))),
        ("CPL", _format_currency(summary.get("cost_per_lead", 0.0))),
        ("CTR", f"{summary.get('click_through_rate', 0.0):.2f}%"),
    ]
    return "".join(
        f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div></div>"
        for label, value in cards
    )


def _campaign_rows(snapshot: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = []
    for campaign in snapshot.get("campaigns", []):
        rows.append(
            [
                campaign.get("campaign_id", ""),
                campaign.get("name", ""),
                campaign.get("channel", ""),
                str(campaign.get("status", "")),
            ]
        )
    return rows


def _lead_rows(leads: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [lead.get("lead_id", ""), lead.get("campaign_id", ""), lead.get("name", ""), lead.get("stage", ""), lead.get("source", "")]
        for lead in leads
    ]


def _metric_rows(metric_snapshots: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [
            snapshot.get("campaign_id", ""),
            _format_currency(float(snapshot.get("spend", 0.0))),
            str(snapshot.get("leads", 0)),
            str(snapshot.get("clicks", 0)),
            str(snapshot.get("impressions", 0)),
            f"{float(snapshot.get('ctr', 0.0)):.2f}%",
            _format_currency(float(snapshot.get("cpl", 0.0))),
        ]
        for snapshot in metric_snapshots
    ]


def _recommendation_rows(snapshot: dict[str, Any], recommendations: list[dict[str, Any]]) -> list[list[str]]:
    return [
        [
            recommendation.get("campaign_name", recommendation.get("campaign_id", "")),
            recommendation.get("campaign_id", ""),
            recommendation.get("action", ""),
            recommendation.get("reason", ""),
            recommendation.get("expected_impact", ""),
            recommendation.get("risk", ""),
        ]
        for recommendation in recommendations
    ]


def build_dashboard(settings: AppSettings) -> gr.Blocks:
    metrics_service = MetricsService(settings)
    initial_state = metrics_service.build_state()

    css = """
    .hero {
        padding: 24px;
        border-radius: 24px;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 100%);
        color: white;
        margin-bottom: 18px;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 12px 0 18px;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 16px;
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #0f172a;
    }
    @media (max-width: 900px) {
        .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    """

    with gr.Blocks(title=settings.app_name) as demo:
        gr.Markdown(
            f"""
            <div class='hero'>
                <h1>{settings.app_name}</h1>
                <p>Small-model dashboard for preschool ad spend, lead flow, and budget pacing. Status: Live (30-min sync cycle)</p>
            </div>
            """
        )

        metrics_html = gr.HTML(value=f"<div class='metric-grid'>{_build_metrics_cards(initial_state['summary'])}</div>")
        insights = gr.Markdown(value=build_insight_text(initial_state["snapshot"], recommend_actions(initial_state["metric_snapshots"], settings.monthly_budget, settings.target_cost_per_lead)))
        gr.Markdown("### AI Coach")
        ai_coach_note = gr.Markdown(value=initial_state["ai_coach_note"])

        with gr.Row():
            refresh_button = gr.Button("Refresh demo data", variant="primary")
            gr.Markdown("Live API sync will be wired here later; this version reads the local demo database.")

        with gr.Tab("Campaigns"):
            campaigns_table = gr.Dataframe(
                headers=["Campaign ID", "Name", "Channel", "Status"],
                datatype=["str", "str", "str", "str"],
                value=_campaign_rows(initial_state["snapshot"]),
                interactive=False,
                wrap=True,
            )

        with gr.Tab("Leads"):
            leads_table = gr.Dataframe(
                headers=["Lead ID", "Campaign ID", "Name", "Stage", "Source"],
                datatype=["str", "str", "str", "str", "str"],
                value=_lead_rows(initial_state["leads"]),
                interactive=False,
                wrap=True,
            )

        with gr.Tab("Metric Snapshots"):
            metric_table = gr.Dataframe(
                headers=["Campaign ID", "Spend", "Leads", "Clicks", "Impressions", "CTR", "CPL"],
                datatype=["str", "str", "str", "str", "str", "str", "str"],
                value=_metric_rows(initial_state["metric_snapshots"]),
                interactive=False,
                wrap=True,
            )

        with gr.Tab("Recommendations"):
            recommendations_table = gr.Dataframe(
                headers=["Campaign", "Campaign ID", "Recommended action", "Reason", "Expected impact", "Risk"],
                datatype=["str", "str", "str", "str", "str", "str"],
                value=_recommendation_rows(initial_state["snapshot"], initial_state["recommendations"]),
                interactive=False,
                wrap=True,
            )

        with gr.Tab("Rules"):
            rules_md = gr.Markdown(
                f"""
                - Monthly budget: {_format_currency(settings.monthly_budget)}
                - Target cost per lead: {_format_currency(settings.target_cost_per_lead)}
                - Low spend threshold: {_format_currency(settings.low_spend_threshold)}
                - High spend threshold: {_format_currency(settings.high_spend_threshold)}
                """
            )

        def refresh() -> tuple[str, str, str, list[list[str]], list[list[str]], list[list[str]], list[list[str]], str]:
            state = metrics_service.refresh()
            actions = recommend_actions(state["metric_snapshots"], settings.monthly_budget, settings.target_cost_per_lead)
            return (
                f"<div class='metric-grid'>{_build_metrics_cards(state['summary'])}</div>",
                build_insight_text(state["snapshot"], actions),
                state["ai_coach_note"],
                _campaign_rows(state["snapshot"]),
                _lead_rows(state["leads"]),
                _metric_rows(state["metric_snapshots"]),
                _recommendation_rows(state["snapshot"], state["recommendations"]),
                rules_md.value,
            )

        refresh_button.click(
            refresh,
            outputs=[metrics_html, insights, ai_coach_note, campaigns_table, leads_table, metric_table, recommendations_table, rules_md],
        )

    return demo
