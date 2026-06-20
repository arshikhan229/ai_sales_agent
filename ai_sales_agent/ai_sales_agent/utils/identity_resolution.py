import frappe


def find_customer_identity(
    phone=None,
    email=None,
    facebook_id=None,
):

    if phone:
        lead = frappe.db.get_value(
            "AI Lead",
            {"custom_phone": phone},
            "name"
        )

        if lead:
            return lead

    if email:
        lead = frappe.db.get_value(
            "AI Lead",
            {"email": email},
            "name"
        )

        if lead:
            return lead

    if facebook_id:
        lead = frappe.db.get_value(
            "AI Lead",
            {"custom_facebook_id": facebook_id},
            "name"
        )

        if lead:
            return lead

    return None


def get_customer_profile(ai_lead_name):

    lead = frappe.get_doc(
        "AI Lead",
        ai_lead_name
    )

    conversations = frappe.get_all(
        "CRM Conversation",
        filters={
            "contact": lead.contact
        },
        fields=[
            "name",
            "channel",
            "direction",
            "message",
            "timestamp"
        ],
        order_by="timestamp desc",
            limit=50
    )

    handoffs = frappe.get_all(
        "AI Handoff",
        filters={
            "lead": lead.name
        },
        fields=[
            "name",
            "status",
            "assigned_to",
            "opportunity"
        ]
    )

    return {
        "lead": {
            "name": lead.name,
            "lead_name": lead.lead_name,
            "email": lead.email,
            "phone": lead.custom_phone,
            "category": lead.lead_category,
            "erp_lead": lead.custom_erp_lead,
            "opportunity": lead.custom_erp_opportunity,
        },
        "conversations": conversations,
        "handoffs": handoffs,
    }
