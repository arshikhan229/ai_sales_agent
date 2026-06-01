import frappe


def build_customer_context(email=None, limit=5):
    """
    Build previous customer interaction context
    """

    if not email:
        return ""

    lead_name = frappe.db.get_value(
        "AI Lead",
        {
            "email": email
        }
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

    context = ""

    for row in interactions:

        context += f"""
Date: {row.get('interaction_date')}
Intent: {row.get('ai_intent')}
Category: {row.get('ai_category')}
Message: {row.get('message')}

"""

    return context.strip()


# Backward compatibility
build_lead_context = build_customer_context