from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any


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
    google_ads_developer_token: str = ""
    google_ads_client_id: str = ""
    google_ads_client_secret: str = ""
    google_ads_refresh_token: str = ""
    google_ads_customer_id: str = ""
    google_ads_login_customer_id: str = ""
    meta_ads_access_token: str = ""
    meta_ads_ad_account_id: str = ""
    llm_provider: str = "local"
    llm_model_path: str = ""
    llm_model_url: str = ""
    llm_temperature: float = 0.2
    llm_max_tokens: int = 220
    llm_context_size: int = 2048


def load_settings() -> AppSettings:
    env = _load_env_file(Path(".env"))
    values = {**env, **os.environ}
    return AppSettings(
        google_ads_developer_token=values.get("GOOGLE_ADS_DEVELOPER_TOKEN", ""),
        google_ads_client_id=values.get("GOOGLE_ADS_CLIENT_ID", ""),
        google_ads_client_secret=values.get("GOOGLE_ADS_CLIENT_SECRET", ""),
        google_ads_refresh_token=values.get("GOOGLE_ADS_REFRESH_TOKEN", ""),
        google_ads_customer_id=values.get("GOOGLE_ADS_CUSTOMER_ID", ""),
        google_ads_login_customer_id=values.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", ""),
        meta_ads_access_token=values.get("META_ADS_ACCESS_TOKEN", ""),
        meta_ads_ad_account_id=values.get("META_ADS_AD_ACCOUNT_ID", ""),
        llm_provider=values.get("LLM_PROVIDER", "local"),
        llm_model_path=values.get("LLM_MODEL_PATH", ""),
        llm_model_url=values.get("LLM_MODEL_URL", ""),
        llm_temperature=float(values.get("LLM_TEMPERATURE", "0.2")),
        llm_max_tokens=int(values.get("LLM_MAX_TOKENS", "220")),
        llm_context_size=int(values.get("LLM_CONTEXT_SIZE", "2048")),
    )


def _load_env_file(env_path: Path) -> dict[str, str]:
    if not env_path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            values[key] = value
    return values
