from dataclasses import dataclass


@dataclass(frozen=True)
class Lead:
    lead_id: str
    campaign_id: str
    name: str
    stage: str
    source: str
    contact: str = ""
    notes: str = ""
