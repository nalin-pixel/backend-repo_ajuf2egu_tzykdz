from typing import List, Dict

# Common interface for provider connectors
# Each connector should implement fetch_reservations(account: dict) -> List[Dict]

class ProviderNotConfigured(Exception):
    pass


def normalize(item: Dict) -> Dict:
    # Ensure basic fields exist
    return {
        "provider": item.get("provider"),
        "category": item.get("category", "other"),
        "title": item.get("title", "Reservation"),
        "location": item.get("location"),
        "start_time": item.get("start_time"),
        "end_time": item.get("end_time"),
        "confirmation_number": item.get("confirmation_number"),
        "details": item.get("details", {}),
        "source": "api",
    }
