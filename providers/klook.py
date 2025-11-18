from typing import List, Dict
from .base import normalize, ProviderNotConfigured


def fetch_reservations(account: Dict) -> List[Dict]:
    token = account.get("access_token")
    if not token:
        raise ProviderNotConfigured("Klook access token missing")
    return [
        normalize({
            "provider": "klook",
            "category": "activity",
            "title": "Hong Kong Disneyland Ticket",
            "location": "Hong Kong",
            "details": {"tickets": 2},
        })
    ]
