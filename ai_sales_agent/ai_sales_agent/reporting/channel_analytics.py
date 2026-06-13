import frappe
from frappe.utils import flt


def _count_handoffs_by_channel(channel):
    return frappe.db.count("AI Handoff", {"channel": channel})


def get_whatsapp_leads():
    return _count_handoffs_by_channel("WhatsApp")


def get_facebook_leads():
    return _count_handoffs_by_channel("Facebook")


def get_email_leads():
    return _count_handoffs_by_channel("Email")


def get_handoff_rate_per_channel():
    # proportion of handoffs created per channel
    total = frappe.db.count("AI Handoff") or 0
    channels = ["WhatsApp", "Facebook", "Email"]
    out = {}
    for c in channels:
        n = _count_handoffs_by_channel(c)
        out[c] = (n / total) * 100.0 if total else 0.0
    return out


def get_conversion_per_channel():
    # use AI Handoff status 'Closed Won' as proxy for conversion
    channels = ["WhatsApp", "Facebook", "Email"]
    out = {}
    for c in channels:
        total = frappe.db.count("AI Handoff", {"channel": c}) or 0
        won = frappe.db.count("AI Handoff", {"channel": c, "status": "Closed Won"}) or 0
        out[c] = (won / total) * 100.0 if total else 0.0
    return out


def get_revenue_per_channel():
    # approximate revenue by summing related Opportunities where AI Handoff channel matches via AI Lead
    try:
        q = """
        SELECT ah.channel, SUM(ifnull(op.expected_revenue,0))
        FROM `tabAI Handoff` ah
        LEFT JOIN `tabAI Lead` al ON al.name = ah.lead
        LEFT JOIN `tabOpportunity` op ON op.opportunity_from = 'Lead' AND op.party_name = al.name
        GROUP BY ah.channel
        """
        rows = frappe.db.sql(q, as_dict=True)
        return {r.channel: flt(r.get('SUM(ifnull(op.expected_revenue,0))') or 0) for r in rows}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "channel_analytics_revenue_error")
        return {}
