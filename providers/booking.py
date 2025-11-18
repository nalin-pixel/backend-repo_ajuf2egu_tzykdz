from typing import List, Dict
import requests
import os
from .base import normalize, ProviderNotConfigured

API_URL = os.getenv("BOOKING_API_URL", "")


def fetch_reservations(account: Dict) -> List[Dict]:
    """
    Demo Booking.com connector (mock).
    In real usage, implement OAuth/token exchange and call provider APIs.
    """
    token = account.get("access_token")
    if not token:
        raise ProviderNotConfigured("Booking access token missing")

    # Placeholder: simulate results instead of real API call
    return [
        normalize({
            "provider": "booking.com",
            "category": "lodging",
            "title": "Hotel Aurora",
            "location": "Rome",
            "start_time": None,
            "end_time": None,
            "confirmation_number": "BK-123456",
            "details": {"nights": 2, "guests": 2},
        })
    ]
