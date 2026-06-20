import frappe


@frappe.whitelist()
def get_handoff_360(handoff):

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    return {
        "name": doc.name,
        "lead": doc.lead,
        "contact": doc.contact,
        "channel": doc.channel,
        "assigned_to": doc.assigned_to,
        "status": doc.status,
        "priority": doc.priority,
        "conversation": doc.conversation,
        "opportunity": doc.opportunity,
        "notes": doc.notes,
        "created_from_intent": doc.created_from_intent,
        "created_from_category": doc.created_from_category,
        "last_followup_at": doc.last_followup_at,
        "followup_count": doc.followup_count,
        "next_followup_due": doc.next_followup_due,
        "sla_status": doc.sla_status,
        "days_open": doc.days_open,
        "ai_suggested_reply": doc.ai_suggested_reply,
        "next_best_action": doc.next_best_action,
        "creation": doc.creation
    }