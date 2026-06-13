"""Helpers to build simple TwiML responses for Twilio voice webhooks.

This module produces minimal, valid TwiML strings suitable for
returning from a Frappe whitelisted endpoint.
"""
from __future__ import annotations

def simple_say_response(message: str) -> str:
    """Return a minimal TwiML <Response><Say>...</Say></Response> string.

    The returned XML is intentionally small and safe to return from a
    whitelisted HTTP endpoint. Twilio will play the message to the
    caller and then execute the remainder of the call flow per your
    Twilio configuration.
    """
    # Escape basic XML entities (keep implementation small and dependency-free)
    esc = (
        message.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )

    return f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<Response>\n  <Say>{esc}</Say>\n</Response>"
