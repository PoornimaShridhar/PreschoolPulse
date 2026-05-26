from dataclasses import dataclass


@dataclass(frozen=True)
class Recommendation:
    campaign_id: str
    campaign_name: str
    action: str
    reason: str
    expected_impact: str
    risk: str
    created_at: str = ""
