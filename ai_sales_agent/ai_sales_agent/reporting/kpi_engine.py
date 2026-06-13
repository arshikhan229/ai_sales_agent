import frappe
from frappe.utils import flt


def get_total_leads():
    return frappe.db.count("AI Lead")


def get_hot_leads():
    return frappe.db.count("AI Lead", {"lead_category": "Hot"})


def get_qualified_leads():
    # consider Hot and Warm as qualified
    return frappe.db.count("AI Lead", {"lead_category": ["in", ["Hot", "Warm", "Qualified"]]})


def get_open_handoffs():
    return frappe.db.count("AI Handoff", {"status": ["!=", "Closed"]})


def get_closed_won():
    # count Opportunities won
    return frappe.db.count("Opportunity", {"status": "Won"})


def get_closed_lost():
    return frappe.db.count("Opportunity", {"status": "Lost"})


def get_total_opportunities():
    return frappe.db.count("Opportunity")


def get_pipeline_value():
    try:
        res = frappe.db.sql("SELECT SUM(expected_revenue) FROM `tabOpportunity`", as_list=True)
        return flt(res[0][0]) if res and res[0][0] is not None else 0.0
    except Exception:
        frappe.log_error(frappe.get_traceback(), "kpi_engine_pipeline_error")
        return 0.0


def get_conversion_rate():
    leads = get_total_leads() or 0
    won = get_closed_won() or 0
    try:
        return (won / leads) * 100.0 if leads else 0.0
    except Exception:
        return 0.0
