from __future__ import annotations

import frappe
from frappe.utils import now_datetime, get_datetime, add_days
from typing import List, Dict, Any

from ai_sales_agent.ai_sales_agent.followup.followup_templates import generate_message


def _get_settings() -> Dict[str, Any]:
    """Read follow-up related settings from `AI Settings` single doc.

    Defaults are conservative to avoid spamming.
    """
    try:
        s = frappe.get_single("AI Settings")
    except Exception:
        # If settings do not exist, return defaults
        return {
            "auto_followup_enabled": False,
            "followup_delay_days": 7,
            "max_followup_attempts": 3,
        }

    return {
        "auto_followup_enabled": bool(getattr(s, "auto_followup_enabled", False)),
        "followup_delay_days": int(getattr(s, "followup_delay_days", 7) or 7),
        "max_followup_attempts": int(getattr(s, "max_followup_attempts", 3) or 3),
    }


def _find_stale_handoffs(delay_days: int) -> List[Dict[str, Any]]:
    """Return AI Handoffs that qualify for follow-up.

    Selection heuristics:
      - status not Closed/Closed Won/Closed Lost
      - either `next_followup_due` is not null and <= cutoff OR `last_followup_at` is null and `creation` <= cutoff
      - followup_count < max attempts will be checked by caller
    """
    cutoff = add_days(get_datetime(), -delay_days)

    # Query for handoffs where status is still open and next_followup_due <= cutoff
    sql = (
        "SELECT name, lead, contact, status, followup_count, last_followup_at, next_followup_due, creation "
        "FROM `tabAI Handoff` "
        "WHERE status NOT IN ('Closed', 'Closed Won', 'Closed Lost') "
        f"AND ( (next_followup_due IS NOT NULL AND next_followup_due <= %(cutoff)s) "
        f"OR (last_followup_at IS NULL AND creation <= %(cutoff)s) )"
    )

    try:
        rows = frappe.db.sql(sql, {"cutoff": cutoff}, as_dict=True)
        return rows
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_find_stale_handoffs_error")
        return []


def _log_followup_activity(handoff_name: str, channel: str, contact: str, message: str) -> None:
    try:
        # create CRM Conversation using conversation logger if available
        try:
            from ai_sales_agent.ai_sales_agent.utils import conversation_logger
            conversation_logger.log_conversation(contact=contact, channel=channel, direction="Outgoing", message=message)
        except Exception:
            # fallback: create minimal CRM Conversation doc
            doc = frappe.get_doc({
                "doctype": "CRM Conversation",
                "contact": contact,
                "channel": channel,
                "direction": "Outgoing",
                "message": message,
                "timestamp": now_datetime(),
            })
            try:
                doc.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "followup_log_conversation_error")

        # Append an AI Lead Interaction row to the AI Lead (if table exists)
        try:
            h = frappe.get_doc("AI Handoff", handoff_name)
            lead_name = h.lead
            if lead_name and frappe.db.exists("AI Lead", lead_name):
                lead = frappe.get_doc("AI Lead", lead_name)
                # ensure table exists on doc
                if hasattr(lead, "ai_lead_interaction"):
                    lead.append("ai_lead_interaction", {
                        "interaction_date": now_datetime(),
                        "source": channel,
                        "message": message,
                    })
                    lead.save(ignore_permissions=True)
                    frappe.db.commit()
        except Exception:
            # non-fatal
            frappe.log_error(frappe.get_traceback(), "followup_log_ai_lead_interaction_error")

    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            "followup_log_followup_activity_error"
        )


def _send_for_handoff(handoff: Dict[str, Any], settings: Dict[str, Any]) -> Dict[str, Any]:
    """Send follow-up for a single handoff over available channels.

    Returns a dict with send results.
    """
    name = handoff.get("name")
    contact = handoff.get("contact") or None
    lead = handoff.get("lead") or None

    # Load lead details for personalization
    lead_doc = None
    lead_info = {"lead_name": None, "icp_score": None, "status": None, "phone": None, "email": None}
    try:
        if lead and frappe.db.exists("AI Lead", lead):
            lead_doc = frappe.get_doc("AI Lead", lead)
            lead_info.update({
                "lead_name": getattr(lead_doc, "lead_name", None),
                "icp_score": getattr(lead_doc, "icp_score", None),
                "status": getattr(lead_doc, "lead_category", None),
                "phone": getattr(lead_doc, "phone", None),
                "email": getattr(lead_doc, "email", None),
            })
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_load_lead_error")

    results = {"sent": [], "failed": []}

    # Try WhatsApp first if contact/phone available
    wa_target = contact or lead_info.get("phone")
    if wa_target:
        msg = generate_message(lead_info, "WhatsApp")
        try:
            from ai_sales_agent.ai_sales_agent.utils import reply_dispatcher
            r = reply_dispatcher.send_reply(channel="WhatsApp", contact=wa_target, message=msg, handoff_name=name)
            if r.get("success"):
                results["sent"].append({"channel": "WhatsApp", "target": wa_target})
                _log_followup_activity(name, "WhatsApp", wa_target, msg)
            else:
                results["failed"].append({"channel": "WhatsApp", "target": wa_target, "error": r})
        except Exception:
            frappe.log_error(frappe.get_traceback(), "followup_send_whatsapp_error")
            results["failed"].append({"channel": "WhatsApp", "target": wa_target})

    # Try Email if lead has email
    email_target = lead_info.get("email")
    if email_target:
        msg = generate_message(lead_info, "Email")
        try:
            from ai_sales_agent.ai_sales_agent.utils import reply_dispatcher
            r = reply_dispatcher.send_reply(channel="Email", contact=email_target, message=msg, handoff_name=name)
            if r.get("success"):
                results["sent"].append({"channel": "Email", "target": email_target})
                _log_followup_activity(name, "Email", email_target, msg)
            else:
                results["failed"].append({"channel": "Email", "target": email_target, "error": r})
        except Exception:
            frappe.log_error(frappe.get_traceback(), "followup_send_email_error")
            results["failed"].append({"channel": "Email", "target": email_target})

    # Update handoff counters to prevent duplicates
    try:
        if name:
            h = frappe.get_doc("AI Handoff", name)
            h.followup_count = (getattr(h, "followup_count", 0) or 0) + 1
            h.last_followup_at = now_datetime()
            # set next follow-up due based on settings
            h.next_followup_due = add_days(h.last_followup_at, int(settings.get("followup_delay_days", 7)))
            h.db_set("followup_count", h.followup_count, update_modified=True)
            h.db_set("last_followup_at", h.last_followup_at, update_modified=True)
            h.db_set("next_followup_due", h.next_followup_due, update_modified=True)
            frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_update_handoff_error")

    return results


def scan_and_send_followups() -> Dict[str, Any]:
    """Main entry point to scan for stale handoffs and send follow-ups.

    Returns a summary dict with counts and details.
    """
    settings = _get_settings()
    if not settings.get("auto_followup_enabled"):
        return {"status": "disabled"}

    delay = settings.get("followup_delay_days", 7)
    max_attempts = settings.get("max_followup_attempts", 3)

    candidates = _find_stale_handoffs(delay)
    summary = {"candidates": len(candidates), "sent": 0, "failed": 0, "details": []}

    for h in candidates:
        try:
            attempts = int(h.get("followup_count") or 0)
            if attempts >= max_attempts:
                continue

            res = _send_for_handoff(h, settings)
            summary_entry = {"handoff": h.get("name"), "result": res}
            summary["details"].append(summary_entry)
            summary["sent"] += len(res.get("sent", []))
            summary["failed"] += len(res.get("failed", []))
        except Exception:
            frappe.log_error(frappe.get_traceback(), "followup_scan_error")

    return summary
