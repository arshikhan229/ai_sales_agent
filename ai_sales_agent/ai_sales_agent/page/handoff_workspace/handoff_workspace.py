import frappe


@frappe.whitelist()
def get_handoff_workspace(handoff):

    doc = frappe.get_doc(
        "AI Handoff",
        handoff
    )

    conversations = frappe.get_all(
        "CRM Conversation",
        filters={
            "contact": doc.contact
        },
        fields=[
            "channel",
            "direction",
            "message",
            "timestamp"
        ],
        order_by="timestamp desc"
    )

    todos = []

    if doc.opportunity:

        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "Opportunity",
                "reference_name": doc.opportunity
            },
            fields=[
                "name",
                "status",
                "allocated_to",
                "creation"
            ]
        )

    return {
        "handoff": doc.as_dict(),
        "conversations": conversations,
        "todos": todos
    }