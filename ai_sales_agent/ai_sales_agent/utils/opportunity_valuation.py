import frappe


INTENT_VALUES = {

    "Pricing Inquiry": 25000,

    "Demo Request": 50000,

    "Implementation Inquiry": 150000,

    "ERPNext Deployment": 300000,

    "Support Request": 10000,

    "General Inquiry": 15000
}


def estimate_opportunity_value(
    intent_type=None,
    lead_category=None
):

    amount = INTENT_VALUES.get(
        intent_type,
        15000
    )

    if lead_category == "Hot":
        amount *= 1.5

    elif lead_category == "Warm":
        amount *= 1.2

    return amount


def apply_opportunity_value(
    opportunity,
    intent_type=None,
    lead_category=None
):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    if (
        doc.opportunity_amount
        and
        doc.opportunity_amount > 0
    ):
        return doc.opportunity_amount

    amount = estimate_opportunity_value(
        intent_type,
        lead_category
    )

    doc.opportunity_amount = amount

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return amount


def apply_default_value(
    opportunity
):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    if (
        doc.opportunity_amount
        and
        doc.opportunity_amount > 0
    ):
        return doc.opportunity_amount

    source = (
        doc.source
        or ""
    ).lower()

    amount = 15000

    if source == "email":
        amount = 25000

    elif source == "whatsapp":
        amount = 35000

    elif source == "facebook":
        amount = 30000

    doc.opportunity_amount = amount

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return amount