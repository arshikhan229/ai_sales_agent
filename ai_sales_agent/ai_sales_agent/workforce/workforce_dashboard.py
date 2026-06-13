import frappe
from frappe import _
from frappe.utils import now_datetime

from ai_sales_agent.ai_sales_agent.workforce.workforce_metrics import (
    assigned_handoffs,
    open_opportunities,
    followups_due,
    sla_breaches,
    closed_won_by_agent,
    closed_lost_by_agent,
    conversion_rate_by_agent,
)


@frappe.whitelist()
def get_workforce_metrics():
    try:
        users = frappe.get_all('User', filters=[['User', 'enabled', '=', 1]], fields=['name'], limit=200)
        summary = {
            'total_assigned_handoffs': 0,
            'total_open_opportunities': 0,
            'total_followups_due': 0,
            'total_sla_breaches': 0,
        }
        for u in users:
            name = u.name
            summary['total_assigned_handoffs'] += assigned_handoffs(name)
            summary['total_open_opportunities'] += open_opportunities(name)
            summary['total_followups_due'] += followups_due(name)
            summary['total_sla_breaches'] += sla_breaches(name)
        return summary
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'get_workforce_metrics_error')
        return {}


@frappe.whitelist()
def get_agent_performance(agent=None):
    try:
        agents = [agent] if agent else [u.name for u in frappe.get_all('User', filters=[['User','enabled','=','1']], fields=['name'], limit=200)]
        out = []
        for a in agents:
            assigned = assigned_handoffs(a)
            open_ops = open_opportunities(a)
            followups = followups_due(a)
            sla = sla_breaches(a)
            closed_won = closed_won_by_agent(a)
            closed_lost = closed_lost_by_agent(a)
            conv = conversion_rate_by_agent(a)
            out.append({
                'agent': a,
                'assigned_handoffs': assigned,
                'open_opportunities': open_ops,
                'followups_due': followups,
                'sla_breaches': sla,
                'closed_won': closed_won,
                'closed_lost': closed_lost,
                'conversion_rate': conv,
            })
        return out
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'get_agent_performance_error')
        return []


@frappe.whitelist()
def get_supervisor_leaderboard(limit=10):
    try:
        rows = frappe.db.sql(
            """
            SELECT assigned_to as agent,
                SUM(CASE WHEN status='Closed Won' THEN 1 ELSE 0 END) as closed_won
            FROM `tabAI Handoff`
            WHERE assigned_to IS NOT NULL
            GROUP BY assigned_to
            ORDER BY closed_won DESC
            LIMIT %s
            """,
            (int(limit),),
            as_dict=True,
        )
        return rows
    except Exception:
        frappe.log_error(frappe.get_traceback(), 'get_supervisor_leaderboard_error')
        return []
