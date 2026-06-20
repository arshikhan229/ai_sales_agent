import frappe


@frappe.whitelist()
def get_activity_feed():

    feed = []

    add_conversations(feed)
    add_handoffs(feed)
    add_todos(feed)

    feed.sort(
        key=lambda x: x.get("timestamp"),
        reverse=True
    )

    return feed[:200]


def add_conversations(feed):

    rows = frappe.get_all(
        "CRM Conversation",
        fields=[
            "name",
            "channel",
            "message",
            "timestamp",
            "custom_ai_lead"
        ],
        order_by="timestamp desc",
        limit=100
    )

    for row in rows:

        feed.append({
            "type": "Conversation",
            "title": row.message,
            "channel": row.channel,
            "lead": row.custom_ai_lead,
            "timestamp": row.timestamp
        })


def add_handoffs(feed):

    rows = frappe.get_all(
        "AI Handoff",
        fields=[
            "name",
            "lead",
            "assigned_to",
            "status",
            "creation"
        ],
        order_by="creation desc",
        limit=100
    )

    for row in rows:

        feed.append({
            "type": "Handoff",
            "title":
                f"Assigned to {row.assigned_to}",
            "lead": row.lead,
            "status": row.status,
            "timestamp": row.creation
        })


def add_todos(feed):

    rows = frappe.get_all(
        "ToDo",
        fields=[
            "name",
            "description",
            "status",
            "creation"
        ],
        order_by="creation desc",
        limit=100
    )

    for row in rows:

        feed.append({
            "type": "ToDo",
            "title": row.description,
            "status": row.status,
            "timestamp": row.creation
        })