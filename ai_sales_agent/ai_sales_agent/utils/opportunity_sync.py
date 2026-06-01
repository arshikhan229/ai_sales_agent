import frappe


def create_opportunity_from_lead(
    erpnext_lead,
    intent_type=None
):
    """
    Create ERPNext Opportunity
    from ERPNext Lead
    """

    if not erpnext_lead:
        return None

    existing = frappe.db.exists(
        "Opportunity",
        {
            "opportunity_from": "Lead",
            "party_name": erpnext_lead.name
        }
    )

    if existing:

        return frappe.get_doc(
            "Opportunity",
            existing
        )

    opportunity_type = "Sales"

    if intent_type in [
        "Support Request",
        "Billing Inquiry",
        "Complaint"
    ]:
        opportunity_type = "Support"

    opportunity = frappe.get_doc({

        "doctype": "Opportunity",

        "opportunity_from":
            "Lead",

        "party_name":
            erpnext_lead.name,

        "customer_name":
            erpnext_lead.lead_name,

        "source":
            erpnext_lead.source,

        "status":
            "Open",

        "opportunity_type":
            opportunity_type,

        "title":
            f"{erpnext_lead.lead_name} Opportunity",

        "contact_email":
            erpnext_lead.email_id
    })

    opportunity.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return opportunity