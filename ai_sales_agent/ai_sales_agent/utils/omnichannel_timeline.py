import frappe


def get_customer_timeline(ai_lead):

    timeline = []

    add_conversations(ai_lead, timeline)
    add_handoffs(ai_lead, timeline)
    add_todos(ai_lead, timeline)
    add_communications(ai_lead, timeline)

    timeline.sort(
        key=lambda x: x.get("timestamp") or "",
        reverse=True
    )

    return timeline


def add_conversations(ai_lead, timeline):

    rows = frappe.get_all(
        "CRM Conversation",
        filters={
            "custom_ai_lead": ai_lead
        },
        fields=[
            "channel",
            "message",
            "timestamp"
        ]
    )

    for row in rows:

        timeline.append({
            "type": "Conversation",
            "channel": row.channel,
            "title": row.message,
            "timestamp": row.timestamp
        })


def add_handoffs(ai_lead, timeline):

    rows = frappe.get_all(
        "AI Handoff",
        filters={
            "lead": ai_lead
        },
        fields=[
            "assigned_to",
            "status",
            "creation"
        ]
    )

    for row in rows:

        timeline.append({
            "type": "Handoff",
            "title": f"Assigned to {row.assigned_to}",
            "status": row.status,
            "timestamp": row.creation
        })


def add_todos(ai_lead, timeline):

    opportunities = frappe.get_all(
        "AI Handoff",
        filters={
            "lead": ai_lead
        },
        pluck="opportunity"
    )

    for opp in opportunities:

        if not opp:
            continue

        todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "Opportunity",
                "reference_name": opp
            },
            fields=[
                "description",
                "status",
                "creation"
            ]
        )

        for todo in todos:

            timeline.append({
                "type": "ToDo",
                "title": todo.description,
                "status": todo.status,
                "timestamp": todo.creation
            })


def add_communications(ai_lead, timeline):

    lead = frappe.get_doc(
        "AI Lead",
        ai_lead
    )

    email = getattr(
        lead,
        "email",
        None
    )

    if not email:
        return

    rows = frappe.get_all(
        "Communication",
        filters={
            "sender": email
        },
        fields=[
            "subject",
            "creation"
        ]
    )

    for row in rows:

        timeline.append({
            "type": "Email",
            "title": row.subject,
            "timestamp": row.creation
        })