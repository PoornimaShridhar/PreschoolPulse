from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    app_name: str = "PreschoolPulse"
    database_path: Path = Path("data/app.db")
    host: str = "127.0.0.1"
    port: int = 7860
    refresh_interval_minutes: int = 30
    monthly_budget: float = 1500.0
    target_cost_per_lead: float = 35.0
    low_spend_threshold: float = 100.0
    high_spend_threshold: float = 400.0


def load_settings() -> AppSettings:
    return AppSettings()
