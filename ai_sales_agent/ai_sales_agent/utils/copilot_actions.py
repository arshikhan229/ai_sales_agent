import frappe


@frappe.whitelist()
def create_followups_for_risky_deals():

    opportunities = frappe.get_all(
        "Opportunity",
        filters={
            "custom_risk_level": "High"
        },
        fields=["name"]
    )

    created = []

    for opp in opportunities:

        exists = frappe.db.exists(
            "ToDo",
            {
                "reference_type": "Opportunity",
                "reference_name": opp.name
            }
        )

        if exists:
            continue

        todo = frappe.get_doc({
            "doctype": "ToDo",
            "description":
                f"AI Followup Required\n\n{opp.name}",
            "reference_type": "Opportunity",
            "reference_name": opp.name,
            "status": "Open",
            "priority": "High"
        })

        todo.insert(ignore_permissions=True)

        created.append(todo.name)

    frappe.db.commit()

    return {
        "created": len(created),
        "todos": created
    }


@frappe.whitelist()
def move_opportunity(
    opportunity,
    stage
):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    doc.custom_pipeline_stage = stage

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True,
        "opportunity": opportunity,
        "stage": stage
    }


@frappe.whitelist()
def close_opportunity(
    opportunity
):

    doc = frappe.get_doc(
        "Opportunity",
        opportunity
    )

    doc.status = "Closed"

    doc.custom_pipeline_stage = "Closed Won"

    doc.save(
        ignore_permissions=True
    )

    frappe.db.commit()

    return {
        "success": True
    }
