from dataclasses import dataclass


@dataclass(frozen=True)
class MetricSnapshot:
    campaign_id: str
    spend: float
    leads: int
    clicks: int
    impressions: int
    ctr: float
    cpl: float
    created_at: str = ""
