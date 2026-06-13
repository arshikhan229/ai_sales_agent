"""Templates for automated follow-up messages.

Keep templates short and personalised; these are used by the follow-up
engine to create channel-specific messages.
"""
from __future__ import annotations

from typing import Dict, Any


def generate_message(lead: Dict[str, Any], channel: str) -> str:
    """Generate a brief, personalised follow-up message.

    lead: dict with keys like `lead_name`, `icp_score`, `status`, `phone`, `email`.
    channel: 'WhatsApp' or 'Email'
    """
    name = lead.get("lead_name") or lead.get("name") or "there"
    icp = lead.get("icp_score")
    status = lead.get("status") or ""

    score_part = f" Our score for fit: {icp}." if icp is not None else ""

    if "whatsapp" in channel.lower():
        return (
            f"Hi {name},\n\nWe haven't heard back about your request for {status}."
            f" I wanted to check if you still need help.{score_part}\n\nReply here and we'll assist promptly.\n\n— Sales Team"
        )

    # Default to email-friendly format
    return (
        f"Hello {name},\n\nI hope you're well. I'm following up regarding your {status} inquiry."
        f"{score_part}\n\nIf you'd like to continue the conversation, reply to this email or message us on WhatsApp.\n\nBest regards,\nSales Team"
    )
