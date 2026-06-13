import frappe
from frappe import _
from frappe.utils import flt, now_datetime

from .kpi_engine import (
    get_total_leads,
    get_hot_leads,
    get_qualified_leads,
    get_open_handoffs,
    get_closed_won,
    get_closed_lost,
    get_total_opportunities,
    get_pipeline_value,
    get_conversion_rate,
)

from .channel_analytics import (
    get_whatsapp_leads,
    get_facebook_leads,
    get_email_leads,
    get_handoff_rate_per_channel,
    get_conversion_per_channel,
    get_revenue_per_channel,
)


@frappe.whitelist()
def get_dashboard_metrics():
    return {
        "total_leads": get_total_leads(),
        "hot_leads": get_hot_leads(),
        "qualified_leads": get_qualified_leads(),
        "opportunities": get_total_opportunities(),
        "opportunities_won": get_closed_won(),
        "opportunities_lost": get_closed_lost(),
        "conversion_rate": get_conversion_rate(),
        "open_handoffs": get_open_handoffs(),
        "pipeline_value": get_pipeline_value(),
    }


@frappe.whitelist()
def get_funnel_metrics():
    # Lead -> Qualified -> Opportunity -> Won
    leads = get_total_leads()
    qualified = get_qualified_leads()
    opportunities = get_total_opportunities()
    won = get_closed_won()
    return {
        "lead": leads,
        "qualified": qualified,
        "opportunity": opportunities,
        "won": won,
    }


@frappe.whitelist()
def get_channel_metrics():
    return {
        "whatsapp_leads": get_whatsapp_leads(),
        "facebook_leads": get_facebook_leads(),
        "email_leads": get_email_leads(),
        "handoff_rate": get_handoff_rate_per_channel(),
        "conversion_per_channel": get_conversion_per_channel(),
        "revenue_per_channel": get_revenue_per_channel(),
    }


@frappe.whitelist()
def get_agent_metrics():
    # Build simple agent performance summary grouped by assigned_to
    try:
        rows = frappe.db.sql(
            """
            SELECT assigned_to as agent,
                COUNT(*) as assigned_leads,
                SUM(CASE WHEN status = 'Closed Won' THEN 1 ELSE 0 END) as closed_won,
                SUM(CASE WHEN status = 'Closed Lost' THEN 1 ELSE 0 END) as closed_lost,
                AVG(ifnull(followup_count,0)) as avg_followups
            FROM `tabAI Handoff`
            GROUP BY assigned_to
            """,
            as_dict=True,
        )
        return rows
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_agent_metrics_error")
        return []


@frappe.whitelist()
def get_sla_metrics():
    # SLA statuses: Healthy, Warning, Breached stored in ai_handoff.sla_status
    try:
        rows = frappe.db.sql(
            "SELECT sla_status, COUNT(*) as count FROM `tabAI Handoff` GROUP BY sla_status",
            as_dict=True,
        )
        return {r.sla_status or 'Unknown': r.count for r in rows}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_sla_metrics_error")
        return {}
