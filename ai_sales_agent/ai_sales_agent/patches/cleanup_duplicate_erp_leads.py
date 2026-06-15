import frappe
from frappe.utils import get_datetime


def execute():
    if not frappe.db.table_exists("Lead"):
        return

    merged = 0
    merged += _merge_duplicate_leads("email_id")
    merged += _merge_duplicate_leads("lead_name")

    frappe.db.commit()
    frappe.logger().info(
        f"cleanup_duplicate_erp_leads merged={merged}"
    )


def _merge_duplicate_leads(fieldname):
    groups = frappe.db.sql(
        f"""
        SELECT `{fieldname}` AS duplicate_key
        FROM `tabLead`
        WHERE `{fieldname}` IS NOT NULL
            AND `{fieldname}` != ''
        GROUP BY `{fieldname}`
        HAVING COUNT(*) > 1
        """,
        as_dict=True,
    )

    merged = 0

    for group in groups:
        leads = frappe.get_all(
            "Lead",
            filters={fieldname: group.duplicate_key},
            fields=["name", "creation"],
            order_by="creation asc",
        )

        if len(leads) < 2:
            continue

        canonical = _choose_canonical_lead(leads)

        for lead in leads:
            if lead.name == canonical:
                continue

            _move_lead_references(
                source_lead=lead.name,
                target_lead=canonical,
            )

            if not _has_blocking_links(lead.name):
                frappe.delete_doc(
                    "Lead",
                    lead.name,
                    ignore_permissions=True,
                    force=True,
                )
                merged += 1

    return merged


def _choose_canonical_lead(leads):
    best = None
    best_score = None

    for lead in leads:
        opportunity_count = frappe.db.count(
            "Opportunity",
            {
                "opportunity_from": "Lead",
                "party_name": lead.name,
            },
        )
        creation = get_datetime(lead.creation)
        score = (opportunity_count, -creation.timestamp())

        if best_score is None or score > best_score:
            best_score = score
            best = lead.name

    return best or leads[0].name


def _move_lead_references(source_lead, target_lead):
    opportunities = frappe.get_all(
        "Opportunity",
        filters={
            "opportunity_from": "Lead",
            "party_name": source_lead,
        },
        pluck="name",
    )

    for opportunity in opportunities:
        frappe.db.set_value(
            "Opportunity",
            opportunity,
            "party_name",
            target_lead,
            update_modified=False,
        )

    conversations = frappe.get_all(
        "CRM Conversation",
        filters={"custom_erp_lead": source_lead},
        pluck="name",
    ) if frappe.db.table_exists("CRM Conversation") and frappe.db.has_column("CRM Conversation", "custom_erp_lead") else []

    for conversation in conversations:
        frappe.db.set_value(
            "CRM Conversation",
            conversation,
            "custom_erp_lead",
            target_lead,
            update_modified=False,
        )


def _has_blocking_links(lead_name):
    return bool(
        frappe.db.exists(
            "Opportunity",
            {
                "opportunity_from": "Lead",
                "party_name": lead_name,
            },
        )
    )
