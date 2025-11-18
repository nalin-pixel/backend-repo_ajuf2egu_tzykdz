import re
from typing import Dict, Optional

# Very lightweight, heuristic parsers for common provider confirmation emails.
# We scan subject + body text and try to extract core fields.

PROVIDER_HINTS = {
    "booking.com": ["booking.com", "Your booking", "Reservation confirmed"],
    "agoda": ["agoda", "Agoda booking", "Agoda reservation"],
    "viator": ["viator", "Viator booking", "Your Viator"],
    "klook": ["klook", "Klook"],
    "getyourguide": ["getyourguide", "GetYourGuide"],
}

DATE_RE = r"(\d{4}-\d{2}-\d{2}|\d{1,2}\s\w{3,9}\s\d{4}|\w{3,9}\s\d{1,2},\s\d{4})"
TIME_RE = r"(\d{1,2}:\d{2}(?:\s?[AP]M)?)"

CONF_RE = r"(confirmation(?:\s|#|\snumber\s|\sno\.)?\s?:?\s?([A-Z0-9\-]{5,}))"

HOTEL_RE = r"(hotel|stay|accommodation)\s?:?\s?([\w\s\-\'&,\.]{3,})"
ACTIVITY_RE = r"(tour|activity|experience|ticket)\s?:?\s?([\w\s\-\'&,\.]{3,})"
LOCATION_RE = r"(in|at|location)\s?:?\s?([\w\s\-\'&,\.]{3,})"


def detect_provider(subject: str, sender: str, body: str) -> Optional[str]:
    text = f"{subject} {sender} {body}".lower()
    for prov, hints in PROVIDER_HINTS.items():
        if any(h.lower() in text for h in hints):
            return prov
    return None


def extract_confirmation(text: str) -> Optional[str]:
    m = re.search(CONF_RE, text, re.IGNORECASE)
    if m:
        return m.group(2).strip()
    return None


def extract_title(text: str) -> Optional[str]:
    # Try hotel then activity
    m = re.search(HOTEL_RE, text, re.IGNORECASE)
    if m:
        return m.group(2).strip()
    m = re.search(ACTIVITY_RE, text, re.IGNORECASE)
    if m:
        return m.group(2).strip()
    # Fallback: first quoted phrase or subject-like token
    q = re.search(r'"([^"]{3,60})"', text)
    if q:
        return q.group(1).strip()
    return None


def extract_dates(text: str):
    # Look for two dates (range), or a single date optionally with times
    dates = re.findall(DATE_RE, text, re.IGNORECASE)
    times = re.findall(TIME_RE, text, re.IGNORECASE)
    start_date = dates[0] if dates else None
    end_date = dates[1] if len(dates) > 1 else None
    start_time = times[0] if times else None
    end_time = times[1] if len(times) > 1 else None
    return start_date, end_date, start_time, end_time


def extract_location(text: str) -> Optional[str]:
    m = re.search(LOCATION_RE, text, re.IGNORECASE)
    if m:
        return m.group(2).strip()
    return None


def parse_email(subject: str, sender: str, body_text: str, provider_hint: Optional[str] = None) -> Optional[Dict]:
    # Decide provider
    provider = (provider_hint or detect_provider(subject, sender, body_text) or "other").lower()

    # Category heuristic
    category = "activity"
    subj_low = subject.lower()
    body_low = body_text.lower()
    if any(k in subj_low + body_low for k in ["hotel", "stay", "accommodation"]):
        category = "lodging"
    elif any(k in subj_low + body_low for k in ["flight", "airlines", "departure", "arrival"]):
        category = "flight"
    elif any(k in subj_low + body_low for k in ["train", "bus", "transfer"]):
        category = "transport"

    conf = extract_confirmation(subject + "\n" + body_text)
    title = extract_title(subject + "\n" + body_text) or subject[:80]
    loc = extract_location(body_text) or extract_location(subject) or None
    d1, d2, t1, t2 = extract_dates(subject + "\n" + body_text)

    details = {
        "sender": sender,
        "raw_subject": subject,
        "provider_detected": provider,
    }

    return {
        "provider": provider,
        "category": category,
        "title": title or "Reservation",
        "location": loc,
        "start_time_hint": f"{d1} {t1}".strip() if d1 or t1 else None,
        "end_time_hint": f"{d2} {t2}".strip() if d2 or t2 else None,
        "confirmation_number": conf,
        "details": details,
        "source": "email",
    }
