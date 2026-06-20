import frappe


@frappe.whitelist()
def get_customer_360(ai_lead):

    lead = frappe.db.get_value(
        "AI Lead",
        ai_lead,
        [
            "name",
            "lead_name",
            "source",
            "lead_category",
            "intent_type",
            "icp_score",
            "custom_erp_lead",
            "custom_erp_opportunity"
        ],
        as_dict=True
    )

    if not lead:
        return {}

    conversations = frappe.get_all(
        "CRM Conversation",
        filters={
            "custom_ai_lead": ai_lead
        },
        fields=[
            "channel",
            "direction",
            "message",
            "ai_reply",
            "intent",
            "timestamp"
        ],
        order_by="timestamp desc",
        limit=20
    )

    handoffs = frappe.get_all(
        "AI Handoff",
        filters={
            "lead": ai_lead
        },
        fields=[
            "assigned_to",
            "status",
            "creation"
        ],
        order_by="creation desc",
        limit=20
    )

    opportunity_data = {}

    if lead.custom_erp_opportunity:

        opportunity_data = frappe.db.get_value(
            "Opportunity",
            lead.custom_erp_opportunity,
            [
                "custom_ai_deal_score",
                "custom_win_probability",
                "custom_risk_level",
                "custom_next_best_action",
                "custom_ai_summary"
            ],
            as_dict=True
        ) or {}

    return {
        "lead": lead,
        "opportunity": opportunity_data,
        "conversations": conversations,
        "handoffs": handoffs
    }