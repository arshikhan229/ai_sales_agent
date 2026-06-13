import frappe
from frappe.utils import now_datetime

try:
    # optional imports if project provides channel-specific senders
    from ai_sales_agent.ai_sales_agent.utils import sales_copilot
except Exception:
    sales_copilot = None


def _log_conversation(contact, channel, message, source="AI Sales Copilot"):
    """Create an outbound CRM Conversation entry."""
    try:
        doc = frappe.get_doc({
            "doctype": "CRM Conversation",
            "contact": contact,
            "channel": channel,
            "direction": "Outgoing",
            "message": message,
            "source": source,
            "timestamp": now_datetime()
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return True
    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_log_conversation_error")
        return False


def _update_handoff_followup(handoff_name):
    """Increment followup_count and update last_followup_at/next_followup_due on AI Handoff.

    This uses simple heuristics; more advanced scheduling is handled by followup_tracker/sla_monitor.
    """
    try:
        if not handoff_name:
            return False

        h = frappe.get_doc("AI Handoff", handoff_name)
        # increment followup_count
        try:
            h.followup_count = (getattr(h, "followup_count", 0) or 0) + 1
        except Exception:
            h.followup_count = 1

        h.last_followup_at = now_datetime()
        # default next follow-up in 2 days
        try:
            from frappe.utils import add_to_date
            h.next_followup_due = add_to_date(h.last_followup_at, days=2)
        except Exception:
            h.next_followup_due = None

        h.db_set("followup_count", h.followup_count, update_modified=True)
        h.db_set("last_followup_at", h.last_followup_at, update_modified=True)
        if getattr(h, "next_followup_due", None):
            h.db_set("next_followup_due", h.next_followup_due, update_modified=True)

        # trigger SLA recalculation if sla_monitor exists
        try:
            from ai_sales_agent.ai_sales_agent.utils import sla_monitor
            sla_monitor.update_sla_status(h)
        except Exception:
            pass

        frappe.db.commit()
        return True
    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_update_handoff_error")
        return False


def send_email_reply(contact, message, subject=None, sender=None):
    """Send an email. Uses Frappe's email API if available."""
    try:
        recipients = contact
        if isinstance(contact, dict):
            recipients = contact.get("email") or contact.get("contact")

        # Use frappe.sendmail when available
        try:
            frappe.sendmail(recipients=recipients, subject=subject or "Reply from Sales Copilot", message=message)
            return True
        except Exception:
            frappe.log_error(frappe.get_traceback(), "reply_dispatcher_send_email_error")
            return False
    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_send_email_error_outer")
        return False


def send_whatsapp_reply(contact, message):
    """Placeholder: integrate with project WhatsApp sender if present."""
    try:
        # Try to call project whatsapp sender if available
        try:
            from ai_sales_agent.ai_sales_agent.utils import whatsapp_sender
            return whatsapp_sender.send_whatsapp(contact, message)
        except Exception:
            # not available: log and return False
            frappe.logger().info("WhatsApp sender not available; skipping send")
            return False
    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_send_whatsapp_error")
        return False


def send_facebook_reply(contact, message):
    """Placeholder: integrate with project Facebook sender if present."""
    try:
        try:
            from ai_sales_agent.ai_sales_agent.utils import facebook_sender
            return facebook_sender.send_facebook(contact, message)
        except Exception:
            frappe.logger().info("Facebook sender not available; skipping send")
            return False
    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_send_facebook_error")
        return False


@frappe.whitelist()
def send_reply(channel=None, contact=None, message=None, handoff_name=None, subject=None):
    """Unified API to send a reply over the given channel, log the conversation, and update follow-up/SLA.

    Args:
        channel: 'Email' | 'WhatsApp' | 'Facebook'
        contact: email address or contact name (CRM Contact)
        message: reply text
        handoff_name: optional AI Handoff document name to update follow-up
    Returns:
        dict: {success: bool, sent: bool, logged: bool}
    """
    if not channel or not contact or not message:
        return {"success": False, "error": "missing_required_args"}

    sent = False
    try:
        if channel.lower().startswith('email'):
            sent = send_email_reply(contact, message, subject=subject)
        elif 'whatsapp' in channel.lower():
            sent = send_whatsapp_reply(contact, message)
        elif 'facebook' in channel.lower():
            sent = send_facebook_reply(contact, message)
        else:
            # unknown channel: try email as fallback
            sent = send_email_reply(contact, message, subject=subject)

        # log conversation (prefer human-readable channel label)
        logged = _log_conversation(contact=contact, channel=channel, message=message)

        # update handoff followup metrics
        updated = False
        if handoff_name:
            updated = _update_handoff_followup(handoff_name)

        return {"success": True, "sent": bool(sent), "logged": bool(logged), "updated": bool(updated)}

    except Exception:
        frappe.log_error(frappe.get_traceback(), "reply_dispatcher_send_reply_error")
        return {"success": False, "error": "exception"}
