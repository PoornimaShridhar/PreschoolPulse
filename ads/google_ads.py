from data.sample_data import build_demo_snapshot


class GoogleAdsClient:
    def fetch_metrics(self) -> dict:
        snapshot = build_demo_snapshot()
        snapshot["source"] = "google-demo"
        return snapshot
