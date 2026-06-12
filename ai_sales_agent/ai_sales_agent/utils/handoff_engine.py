import frappe


def assign_sales_person(opportunity):

    user = "Administrator"

    if not opportunity:
        return user

    frappe.share.add(
        "Opportunity",
        opportunity,
        user=user,
        write=1,
        share=1,
        notify=0
    )

    return user


def create_followup_todo(
    opportunity,
    assigned_user,
    ai_lead=None
):

    if not opportunity:
        return None

    existing = frappe.db.exists(
        "ToDo",
        {
            "reference_type": "Opportunity",
            "reference_name": opportunity,
            "allocated_to": assigned_user
        }
    )

    if existing:
        return existing

    todo = frappe.get_doc({
        "doctype": "ToDo",
        "allocated_to": assigned_user,
        "description":
            f"Hot Lead Follow-up\n\n"
            f"Opportunity: {opportunity}",
        "reference_type": "Opportunity",
        "reference_name": opportunity,
        "priority": "High",
        "status": "Open"
    })

    todo.insert(ignore_permissions=True)

    frappe.db.commit()

    return todo.name


def notify_sales_team(
    assigned_user,
    opportunity
):

    frappe.publish_realtime(
        "msgprint",
        {
            "title": "🔥 Hot Lead Assigned",
            "message":
                f"Opportunity {opportunity} assigned to you."
        },
        user=assigned_user
    )


def trigger_handoff(
    ai_lead=None,
    erp_lead=None,
    opportunity=None
):

    if not opportunity:
        return

    assigned_user = assign_sales_person(
        opportunity
    )

    create_followup_todo(
        opportunity=opportunity,
        assigned_user=assigned_user,
        ai_lead=ai_lead
    )

    notify_sales_team(
        assigned_user,
        opportunity
    )