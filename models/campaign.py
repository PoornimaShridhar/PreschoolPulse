from dataclasses import dataclass


@dataclass(frozen=True)
class Campaign:
    campaign_id: str
    name: str
    channel: str
    status: str
