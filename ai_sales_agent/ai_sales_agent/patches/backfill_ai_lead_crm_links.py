import frappe

from ai_sales_agent.ai_sales_agent.utils.erpnext_crm_sync import (
    sync_hot_lead_to_crm
)


def execute():

    frappe.logger().info(
        "STARTING AI LEAD CRM LINK BACKFILL"
    )

    hot_leads = frappe.get_all(
        "AI Lead",
        filters={
            "lead_category": "Hot"
        },
        pluck="name"
    )

    updated = 0
    skipped = 0
    failed = 0

    for lead_name in hot_leads:

        try:

            lead = frappe.get_doc(
                "AI Lead",
                lead_name
            )

            # Already linked
            if (
                lead.custom_erp_lead
                and
                lead.custom_erp_opportunity
            ):
                skipped += 1
                continue

            crm_result = sync_hot_lead_to_crm(
                lead
            )

            if not crm_result:
                failed += 1
                continue

            lead.custom_erp_lead = crm_result.get(
                "erp_lead"
            )

            lead.custom_erp_opportunity = crm_result.get(
                "erp_opportunity"
            )

            lead.custom_last_crm_sync = (
                frappe.utils.now_datetime()
            )

            lead.flags.ignore_version = True

            lead.save(
                ignore_permissions=True
            )

            updated += 1

            frappe.logger().info(
                f"""
                AI LEAD BACKFILLED

                Lead:
                {lead.name}

                ERP Lead:
                {lead.custom_erp_lead}

                Opportunity:
                {lead.custom_erp_opportunity}
                """
            )

        except Exception:

            failed += 1

            frappe.log_error(
                frappe.get_traceback(),
                f"AI LEAD BACKFILL ERROR: {lead_name}"
            )

    frappe.db.commit()

    frappe.logger().info(
        f"""
        AI LEAD CRM LINK BACKFILL COMPLETED

        Updated: {updated}
        Skipped: {skipped}
        Failed: {failed}
        """
    )