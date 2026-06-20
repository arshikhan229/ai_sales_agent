import frappe


@frappe.whitelist()
def get_dashboard_data():

    total_leads = frappe.db.count("AI Lead")

    hot_leads = frappe.db.count(
        "AI Lead",
        {
            "lead_category": "Hot"
        }
    )

    open_opportunities = frappe.db.count(
        "Opportunity",
        {
            "status": "Open"
        }
    )

    closed_opportunities = frappe.db.count(
        "Opportunity",
        {
            "status": "Closed"
        }
    )

    open_handoffs = frappe.db.count(
        "AI Handoff",
        {
            "status": "Open"
        }
    )

    followups_due = frappe.db.count(
        "ToDo",
        {
            "status": "Open"
        }
    )

    pipeline_value = frappe.db.sql("""
        select ifnull(sum(opportunity_amount),0)
        from `tabOpportunity`
        where status='Open'
    """)[0][0] or 0

    return {
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "open_opportunities": open_opportunities,
        "closed_opportunities": closed_opportunities,
        "open_handoffs": open_handoffs,
        "followups_due": followups_due,
        "pipeline_value": pipeline_value
    }