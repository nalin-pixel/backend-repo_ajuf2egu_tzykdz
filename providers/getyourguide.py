from typing import List, Dict
from .base import normalize, ProviderNotConfigured


def fetch_reservations(account: Dict) -> List[Dict]:
    token = account.get("access_token")
    if not token:
        raise ProviderNotConfigured("GetYourGuide access token missing")
    return [
        normalize({
            "provider": "getyourguide",
            "category": "activity",
            "title": "Vatican Museums Skip-the-Line",
            "location": "Vatican City",
            "details": {"participants": 2},
        })
    ]
