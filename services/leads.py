from data.db import add_lead, list_leads


class LeadService:
    def __init__(self, database_path) -> None:
        self.database_path = database_path

    def create_lead(self, name: str, contact: str, source: str, stage: str, notes: str) -> list[dict]:
        add_lead(
            self.database_path,
            {
                "name": name,
                "contact": contact,
                "source": source,
                "stage": stage,
                "notes": notes,
            },
        )
        return list_leads(self.database_path)
