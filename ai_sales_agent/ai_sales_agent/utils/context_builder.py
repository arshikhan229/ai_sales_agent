import frappe


def build_lead_context(email=None, limit=5):
    """
    Build previous interaction context for AI
    """

    if not email:
        return ""

    lead_name = frappe.db.get_value(
        "AI Lead",
        {"email": email},
        "name"
    )

    if not lead_name:
        return ""

    interactions = frappe.get_all(
        "AI Lead Interaction",
        filters={
            "parent": lead_name
        },
        fields=[
            "interaction_date",
            "message",
            "ai_intent",
            "ai_category"
        ],
        order_by="interaction_date desc",
        limit=limit
    )

    if not interactions:
        return ""

    context = "Previous Customer Interactions:\n\n"

    for idx, row in enumerate(interactions, start=1):

        context += (
            f"{idx}. "
            f"Message: {row.message}\n"
            f"Intent: {row.ai_intent}\n"
            f"Category: {row.ai_category}\n\n"
        )

    return context