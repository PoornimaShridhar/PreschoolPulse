from data.sample_data import build_demo_snapshot


class MetaAdsClient:
    def fetch_metrics(self) -> dict:
        return build_demo_snapshot()
