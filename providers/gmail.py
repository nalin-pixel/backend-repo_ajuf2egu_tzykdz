import base64
from typing import List, Dict, Optional

from .email_parsers import parse_email

# NOTE: This is a lightweight Gmail scraper using Gmail API via OAuth2 tokens.
# In this environment we mock the Gmail API call and expect raw messages to be
# provided via `raw_eml_list` for demo/testing. For production, swap `fetch_messages`
# to real Google API client usage.

class GmailNotConfigured(Exception):
    pass


def decode_base64url(data: str) -> bytes:
    data += '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data.encode('utf-8'))


def fetch_messages(account: dict, query: Optional[str] = None, raw_eml_list: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Returns list of messages with fields: subject, from, snippet, body_text
    If raw_eml_list is provided, treat it as already fetched list.
    """
    if raw_eml_list is not None:
        return raw_eml_list

    # Mock fallback: return empty to avoid external calls.
    return []


def extract_body_text(payload_parts: List[Dict]) -> str:
    body = []
    def walk(parts):
        for p in parts:
            mime = p.get('mimeType', '')
            data = p.get('body', {}).get('data')
            if data:
                try:
                    text = decode_base64url(data).decode('utf-8', errors='ignore')
                    if mime.startswith('text/plain') or mime.startswith('text/html'):
                        body.append(text)
                except Exception:
                    pass
            if 'parts' in p:
                walk(p['parts'])
    walk(payload_parts)
    return "\n".join(body)[:20000]


def messages_to_reservations(messages: List[Dict], provider_hint: Optional[str] = None) -> List[Dict]:
    out: List[Dict] = []
    for msg in messages:
        subject = msg.get('subject', '')
        sender = msg.get('from', '')
        body_text = msg.get('body_text', msg.get('snippet', ''))
        parsed = parse_email(subject, sender, body_text, provider_hint=provider_hint)
        if parsed:
            out.append(parsed)
    return out
