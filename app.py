from config.settings import load_settings
from data.db import initialize_database, seed_demo_content
from ui.dashboard import build_dashboard
import gradio as gr


def main() -> None:
    settings = load_settings()
    initialize_database(settings.database_path)
    seed_demo_content(settings.database_path)
    demo = build_dashboard(settings)
    demo.launch(server_name=settings.host, server_port=settings.port, share=False, css="""
    .hero {
        padding: 24px;
        border-radius: 24px;
        background: linear-gradient(135deg, #f8fafc 0%, #dbeafe 52%, #eff6ff 100%);
        color: #0f172a;
        border: 1px solid #bfdbfe;
        box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
        margin-bottom: 18px;
    }
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        margin: 12px 0 18px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
    }
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #475569;
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
    """, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
