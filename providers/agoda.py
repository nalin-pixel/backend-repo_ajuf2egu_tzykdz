from typing import List, Dict
from .base import normalize, ProviderNotConfigured


def fetch_reservations(account: Dict) -> List[Dict]:
    token = account.get("access_token")
    if not token:
        raise ProviderNotConfigured("Agoda access token missing")
    return [
        normalize({
            "provider": "agoda",
            "category": "lodging",
            "title": "Seaside Inn",
            "location": "Phuket",
            "confirmation_number": "AG-778899",
            "details": {"nights": 3, "guests": 2},
        })
    ]
