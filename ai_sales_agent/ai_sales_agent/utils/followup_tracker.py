import frappe
from frappe.utils import now, get_datetime, add_days


@frappe.whitelist()
def record_followup(handoff_name):
    """Record a follow-up activity for the given AI Handoff.

    Increments followup_count, updates last_followup_at, sets next_followup_due,
    and transitions status to `Followed Up` after first activity.
    """
    if not handoff_name:
        return {"status": "error", "message": "missing handoff_name"}

    try:
        h = frappe.get_doc("AI Handoff", handoff_name)

        # increment count
        h.followup_count = (h.followup_count or 0) + 1
        h.last_followup_at = now()

        # default next follow-up due in 2 days
        h.next_followup_due = add_days(get_datetime(), 2)

        # status transition: Assigned -> Followed Up
        if (h.status or "").strip().lower() in ("assigned", "open", "waiting follow-up"):
            h.status = "Followed Up"

        h.save(ignore_permissions=True)
        frappe.db.commit()

        return {"status": "success", "handoff": handoff_name}

    except Exception:
        frappe.log_error(frappe.get_traceback(), "record_followup_error")
        return {"status": "error", "message": "exception"}


@frappe.whitelist()
def update_followup_metrics(handoff_name):
    """Recalculate follow-up related metrics (followup_count, days_open).
    Use this to repair metrics when needed.
    """
    if not handoff_name:
        return {"status": "error", "message": "missing handoff_name"}

    try:
        h = frappe.get_doc("AI Handoff", handoff_name)
        created = h.creation
        if created:
            days_open = (frappe.utils.now_datetime() - frappe.utils.get_datetime(created)).days
            h.days_open = max(0, days_open)

        h.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success", "handoff": handoff_name}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "update_followup_metrics_error")
        return {"status": "error"}


@frappe.whitelist()
def mark_qualified(handoff_name):
    if not handoff_name:
        return {"status": "error"}
    try:
        h = frappe.get_doc("AI Handoff", handoff_name)
        h.status = "Qualified"
        h.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "mark_qualified_error")
        return {"status": "error"}


@frappe.whitelist()
def mark_closed_won(handoff_name):
    if not handoff_name:
        return {"status": "error"}
    try:
        h = frappe.get_doc("AI Handoff", handoff_name)
        h.status = "Closed Won"
        h.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "mark_closed_won_error")
        return {"status": "error"}


@frappe.whitelist()
def mark_closed_lost(handoff_name):
    if not handoff_name:
        return {"status": "error"}
    try:
        h = frappe.get_doc("AI Handoff", handoff_name)
        h.status = "Closed Lost"
        h.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "success"}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "mark_closed_lost_error")
        return {"status": "error"}


# Document event helpers
def on_communication(doc, method):
    """Doc event: Communication.after_insert"""
    try:
        contact = getattr(doc, "contact", None)
        if not contact:
            return
        ai_lead = frappe.db.get_value("AI Lead", {"contact": contact}, "name")
        if not ai_lead:
            return
        handoffs = frappe.get_all("AI Handoff", filters=[["AI Handoff", "lead", "=", ai_lead], ["AI Handoff", "status", "!=", "Closed"]], fields=["name"], limit=1)
        if handoffs:
            record_followup(handoffs[0].name)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_on_communication_error")


def on_todo_update(doc, method):
    """Doc event: ToDo.on_update — when a ToDo is marked completed, record follow-up."""
    try:
        if getattr(doc, "status", "") != "Closed":
            return
        # If ToDo references AI Handoff
        if getattr(doc, "reference_type", "") == "AI Handoff" and getattr(doc, "reference_name", None):
            record_followup(doc.reference_name)

        # If ToDo references Opportunity, find handoff for that opportunity
        if getattr(doc, "reference_type", "") == "Opportunity" and getattr(doc, "reference_name", None):
            h = frappe.get_all("AI Handoff", filters={"opportunity": doc.reference_name}, fields=["name"], limit=1)
            if h:
                record_followup(h[0].name)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_on_todo_error")


def on_opportunity_update(doc, method):
    try:
        # Any meaningful update to Opportunity triggers follow-up record for matching handoff
        h = frappe.get_all("AI Handoff", filters={"opportunity": doc.name}, fields=["name"], limit=1)
        if h:
            record_followup(h[0].name)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_on_opportunity_error")


def on_comment(doc, method):
    try:
        # Comment can be linked to AI Handoff via comment.reference_doctype/name
        if getattr(doc, "reference_doctype", "") == "AI Handoff" and getattr(doc, "reference_name", None):
            record_followup(doc.reference_name)
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_on_comment_error")
