import frappe

from ai_sales_agent.ai_sales_agent.utils.opportunity_sync import (
    create_opportunity_from_lead
)


def create_erpnext_lead(ai_lead):
    """
    Create ERPNext Lead from qualified AI Lead
    """

    if not ai_lead:
        return None

    if ai_lead.email:

        existing = frappe.db.exists(
            "Lead",
            {
                "email_id": ai_lead.email
            }
        )

        if existing:
            return frappe.get_doc(
                "Lead",
                existing
            )

    lead = frappe.get_doc({

        "doctype": "Lead",

        "lead_name":
            ai_lead.lead_name,

        "email_id":
            ai_lead.email,

        "company_name":
            ai_lead.company,

        "source":
            ai_lead.source,

        "status":
            "Lead"

    })

    lead.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return lead


def sync_hot_lead_to_crm(
    ai_lead
):
    """
    AI Lead
      ↓
    ERPNext Lead
      ↓
    ERPNext Opportunity
    """

    erp_lead = create_erpnext_lead(
        ai_lead
    )

    if not erp_lead:
        return None

    if ai_lead.intent_type in [

        "Pricing Inquiry",

        "Demo Request",

        "Product Inquiry",

        "Partnership Inquiry"

    ]:

        create_opportunity_from_lead(
            erp_lead,
            ai_lead.intent_type
        )

    return erp_lead