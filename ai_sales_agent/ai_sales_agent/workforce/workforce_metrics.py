import frappe
from frappe.utils import now_datetime


def _count_handoffs(filters=None):
    filters = filters or []
    try:
        return frappe.db.count("AI Handoff", filters) if isinstance(filters, dict) else len(frappe.get_all("AI Handoff", filters=filters, pluck='name'))
    except Exception:
        frappe.log_error(frappe.get_traceback(), "workforce_count_handoffs_error")
        return 0


def assigned_handoffs(user):
    return _count_handoffs([["AI Handoff", "assigned_to", "=", user], ["AI Handoff", "status", "!=", "Closed"]])


def open_opportunities(user=None):
    # optionally filter by owner/assigned user
    filters = [["Opportunity", "docstatus", "=", 1], ["Opportunity", "status", "not in", ["Lost", "Won"]]]
    if user:
        filters.append(["Opportunity", "owner", "=", user])
    try:
        return len(frappe.get_all("Opportunity", filters=filters, pluck='name'))
    except Exception:
        frappe.log_error(frappe.get_traceback(), "workforce_open_opps_error")
        return 0


def followups_due(user=None):
    today = now_datetime().date()
    filters = [["AI Handoff", "next_followup_due", "<=", today], ["AI Handoff", "status", "!=", "Closed"]]
    if user:
        filters.insert(0, ["AI Handoff", "assigned_to", "=", user])
    return _count_handoffs(filters)


def sla_breaches(user=None):
    filters = [["AI Handoff", "sla_status", "=", "Breached"]]
    if user:
        filters.insert(0, ["AI Handoff", "assigned_to", "=", user])
    return _count_handoffs(filters)


def closed_won_by_agent(user=None):
    filters = [["AI Handoff", "status", "=", "Closed Won"]]
    if user:
        filters.insert(0, ["AI Handoff", "assigned_to", "=", user])
    return _count_handoffs(filters)


def closed_lost_by_agent(user=None):
    filters = [["AI Handoff", "status", "=", "Closed Lost"]]
    if user:
        filters.insert(0, ["AI Handoff", "assigned_to", "=", user])
    return _count_handoffs(filters)


def conversion_rate_by_agent(user):
    try:
        assigned = assigned_handoffs(user) or 0
        won = closed_won_by_agent(user) or 0
        return (won / assigned) * 100.0 if assigned else 0.0
    except Exception:
        frappe.log_error(frappe.get_traceback(), "workforce_conversion_error")
        return 0.0
