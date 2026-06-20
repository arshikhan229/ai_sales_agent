import frappe


@frappe.whitelist()
def get_customer_profile_data(ai_lead):

    from ai_sales_agent.ai_sales_agent.utils.identity_resolution import (
        get_customer_profile
    )

    return get_customer_profile(ai_lead)


@frappe.whitelist()
def get_timeline(contact):

    from ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox import (
        get_contact_timeline
    )

    return get_contact_timeline(contact)

@frappe.whitelist()
def get_omnichannel_timeline(
    ai_lead
):

    from ai_sales_agent.ai_sales_agent.utils.omnichannel_timeline import (
        get_customer_timeline
    )

    return get_customer_timeline(
        ai_lead
    )


@frappe.whitelist()
def find_customer_by_contact(contact):

    if not contact:
        return None

    ai_lead = frappe.db.get_value(
        "AI Lead",
        {
            "contact": contact
        },
        "name"
    )

    if ai_lead:
        return ai_lead

    ai_lead = frappe.db.get_value(
        "AI Lead",
        {
            "lead_name": contact
        },
        "name"
    )

    return ai_lead