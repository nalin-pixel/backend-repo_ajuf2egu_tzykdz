from typing import List, Dict
from .base import normalize, ProviderNotConfigured


def fetch_reservations(account: Dict) -> List[Dict]:
    token = account.get("access_token")
    if not token:
        raise ProviderNotConfigured("Viator access token missing")
    return [
        normalize({
            "provider": "viator",
            "category": "activity",
            "title": "Colosseum Guided Tour",
            "location": "Rome",
            "details": {"duration": "3h"},
        })
    ]
