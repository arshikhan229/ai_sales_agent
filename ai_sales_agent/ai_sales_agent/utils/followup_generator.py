import frappe


@frappe.whitelist()
def generate_followup(opportunity):

    opp = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    stage = (
        opp.custom_pipeline_stage
        or "Qualified"
    )

    action_map = {
        "Qualified":
            "Contact lead",

        "Discovery":
            "Schedule discovery call",

        "Proposal":
            "Send proposal reminder",

        "Negotiation":
            "Follow up on pricing",

        "Closed Won":
            "Begin onboarding",

        "Closed Lost":
            "Archive opportunity"
    }

    next_action = action_map.get(
        stage,
        "Follow up"
    )

    email_draft = f"""
Hi,

Thank you for your interest.

We would like to discuss your requirements
and help you move forward.

Regards
Sales Team
"""

    whatsapp_draft = (
        "Hi, just following up regarding "
        "your requirements. Let us know "
        "a convenient time to connect."
    )

    return {
        "next_action": next_action,
        "email_draft": email_draft,
        "whatsapp_draft": whatsapp_draft
    }
@frappe.whitelist()
def create_followup_task(opportunity):

    result = generate_followup(
        opportunity
    )

    todo = frappe.get_doc({
        "doctype": "ToDo",
        "description":
            result["next_action"],
        "reference_type":
            "Opportunity",
        "reference_name":
            opportunity
    })

    todo.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return todo.name