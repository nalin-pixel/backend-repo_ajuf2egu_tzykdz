from typing import List, Dict, Optional
from datetime import datetime

from .gmail import fetch_messages, messages_to_reservations
from .base import normalize


def import_gmail_to_reservations(account: dict, provider_hint: Optional[str] = None, raw_messages: Optional[List[Dict]] = None) -> List[Dict]:
    messages = fetch_messages(account, raw_eml_list=raw_messages)
    reservations = messages_to_reservations(messages, provider_hint=provider_hint)

    normalized = []
    for r in reservations:
        item = {
            **normalize({
                "provider": r.get("provider", "email"),
                "category": r.get("category", "other"),
                "title": r.get("title", "Reservation"),
                "location": r.get("location"),
                "confirmation_number": r.get("confirmation_number"),
                "details": r.get("details", {}),
            }),
            "source": "email",
        }

        # Attach hints to details for future refinement
        st = r.get("start_time_hint")
        et = r.get("end_time_hint")
        if st or et:
            item.setdefault("details", {})
            item["details"].update({"start_time_hint": st, "end_time_hint": et})

        # Try naive datetime parsing for ISO-like strings
        for key in ("start_time_hint", "end_time_hint"):
            val = item.get("details", {}).get(key)
            if isinstance(val, str):
                try:
                    # Very permissive parse: try fromisoformat if close to ISO
                    if len(val) >= 10 and val[:10].count("-") == 2:
                        dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                        if key == "start_time_hint":
                            item["start_time"] = dt
                        else:
                            item["end_time"] = dt
                except Exception:
                    pass

        normalized.append(item)

    return normalized
