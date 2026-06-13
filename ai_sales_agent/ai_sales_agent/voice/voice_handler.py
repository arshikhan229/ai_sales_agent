from __future__ import annotations

import frappe
from typing import Dict, Any

def normalize_phone(raw: str) -> str:
    """Normalize a caller phone number into an international form.

    This function follows the same lightweight approach used by other
    senders in the package: strip whitespace, remove common prefixes
    and ensure a leading `+` for E.164-like formatting. It does not
    attempt to do full validation or formatting (use libphonenumber in
    future if needed).
    """
    if not raw:
        return ""
    p = raw.strip()
    p = p.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    # remove twilio prefixes like "client:" or "whatsapp:" if present
    if ":" in p:
        p = p.split(":", 1)[-1]
    if p and not p.startswith("+"):
        p = f"+{p}"
    return p


def create_or_get_lead(phone: str) -> str:
    """Find an existing Lead or Contact by phone; otherwise create an `AI Lead`.

    Returns the name of the created or found lead record (prefer Contact, then Lead, then AI Lead).
    """
    # Try Contact first
    contact = frappe.db.get_value("Contact", {"mobile_no": phone}) or frappe.db.get_value(
        "Contact", {"phone": phone}
    )
    if contact:
        return contact

    # Try standard Lead
    lead = frappe.db.get_value("Lead", {"mobile_no": phone}) or frappe.db.get_value(
        "Lead", {"phone": phone}
    )
    if lead:
        return lead

    # Otherwise create an AI Lead (lightweight record that links into AI flows)
    ai_lead = None
    try:
        ai_lead = frappe.get_doc(
            {
                "doctype": "AI Lead",
                "lead_name": f"Voice: {phone}",
                "phone": phone,
            }
        )
        ai_lead.insert(ignore_permissions=True)
        frappe.db.commit()
        return ai_lead.name
    except Exception:
        frappe.log_error(frappe.get_traceback(), "voice.create_or_get_lead")
        # As a fallback return the phone string so callers have something
        return phone


def build_call_metadata(form: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "CallSid": form.get("CallSid"),
        "CallStatus": form.get("CallStatus"),
        "To": form.get("To"),
    }
