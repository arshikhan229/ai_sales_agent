import frappe


@frappe.whitelist()
def get_sla_dashboard():

    handoffs = frappe.get_all(
        "AI Handoff",
        fields=[
            "name",
            "lead",
            "assigned_to",
            "status",
            "priority",
            "followup_count",
            "days_open",
            "next_followup_due",
            "sla_status"
        ],
        order_by="days_open desc",
        limit=500
    )

    total = len(handoffs)

    breached = len([
        x for x in handoffs
        if x.get("sla_status") == "Breached"
    ])

    overdue = len([
        x for x in handoffs
        if x.get("days_open", 0) > 3
    ])

    return {
        "summary": {
            "total": total,
            "breached": breached,
            "overdue": overdue
        },
        "handoffs": handoffs
    }