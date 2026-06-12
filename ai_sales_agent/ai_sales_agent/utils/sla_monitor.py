import frappe
from frappe.utils import now_datetime
from datetime import timedelta


def calculate_sla(handoff):
    """Return sla_status string based on time since creation or last follow-up.

    Rules:
    - Healthy: < 24 hours
    - Warning: 24-48 hours
    - Breached: > 48 hours
    """
    try:
        reference_time = handoff.last_followup_at or handoff.creation
        if not reference_time:
            return "Breached"

        delta = now_datetime() - frappe.utils.get_datetime(reference_time)
        hours = delta.total_seconds() / 3600.0

        if hours < 24:
            return "Healthy"
        if hours < 48:
            return "Warning"
        return "Breached"
    except Exception:
        return "Breached"


def get_sla_color(handoff):
    s = calculate_sla(handoff)
    if s == "Healthy":
        return "green"
    if s == "Warning":
        return "orange"
    return "red"


def update_sla_status(handoff):
    try:
        h = handoff
        status = calculate_sla(h)
        h.sla_status = status
        # days_open from creation
        created = h.creation
        if created:
            days_open = (now_datetime() - frappe.utils.get_datetime(created)).days
            h.days_open = max(0, days_open)
        h.save(ignore_permissions=True)
        return True
    except Exception:
        frappe.log_error(frappe.get_traceback(), "update_sla_status_error")
        return False


def run_sla_checks():
    """Scheduled job: run hourly to update SLA status for open handoffs."""
    try:
        handoffs = frappe.get_all("AI Handoff", filters={"status": ["!=", "Closed"]}, fields=["name"] )
        for h in handoffs:
            doc = frappe.get_doc("AI Handoff", h.name)
            update_sla_status(doc)
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "run_sla_checks_error")
