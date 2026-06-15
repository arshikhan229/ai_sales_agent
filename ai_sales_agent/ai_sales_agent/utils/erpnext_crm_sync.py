import frappe

from ai_sales_agent.ai_sales_agent.utils.opportunity_sync import (
    create_opportunity_from_lead
)


def create_erpnext_lead(ai_lead):

    if not ai_lead:
        return None

    # =================================
    # EMAIL MATCH
    # =================================

    if ai_lead.email:

        existing = frappe.db.exists(
            "Lead",
            {
                "email_id": ai_lead.email
            }
        )

        if existing:

            lead = frappe.get_doc(
                "Lead",
                existing
            )

            update_mobile_if_missing(
                lead,
                ai_lead
            )

            return lead

    # =================================
    # LEAD NAME MATCH
    # =================================

    if ai_lead.lead_name:

        existing = frappe.db.exists(
            "Lead",
            {
                "lead_name": ai_lead.lead_name
            }
        )

        if existing:

            lead = frappe.get_doc(
                "Lead",
                existing
            )

            update_mobile_if_missing(
                lead,
                ai_lead
            )

            return lead

    # =================================
    # CONTACT PHONE
    # =================================

    mobile_no = None

    if ai_lead.contact:

        mobile_no = frappe.db.get_value(
            "Contact",
            ai_lead.contact,
            "mobile_no"
        )

    # =================================
    # CREATE ERP LEAD
    # =================================

    lead = frappe.get_doc({

        "doctype": "Lead",

        "lead_name":
            ai_lead.lead_name,

        "email_id":
            ai_lead.email,

        "mobile_no":
            mobile_no,

        "company_name":
            getattr(
                ai_lead,
                "company",
                None
            ),

        "source":
            ai_lead.source,

        "status":
            "Lead"
    })

    lead.insert(
        ignore_permissions=True
    )

    return lead


def update_mobile_if_missing(
    erp_lead,
    ai_lead
):

    if erp_lead.mobile_no:
        return

    if not ai_lead.contact:
        return

    mobile_no = frappe.db.get_value(
        "Contact",
        ai_lead.contact,
        "mobile_no"
    )

    if not mobile_no:
        return

    erp_lead.mobile_no = mobile_no

    erp_lead.save(
        ignore_permissions=True
    )


def sync_hot_lead_to_crm(ai_lead):

    if not ai_lead:
        return None

    erp_lead = create_erpnext_lead(
        ai_lead
    )

    if not erp_lead:
        return None

    opportunity = None

    if ai_lead.lead_category == "Hot":

        opportunity = create_opportunity_from_lead(
            erp_lead,
            ai_lead.intent_type
        )

    return {
        "erp_lead": erp_lead.name,
        "erp_opportunity":
            opportunity.name
            if opportunity
            else None
    }