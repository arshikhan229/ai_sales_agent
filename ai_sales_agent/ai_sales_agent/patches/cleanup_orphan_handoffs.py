import frappe


def execute():
    if not frappe.db.table_exists("AI Handoff"):
        return

    if not frappe.db.table_exists("AI Lead"):
        return

    rows = frappe.db.sql(
        """
        SELECT h.name
        FROM `tabAI Handoff` h
        LEFT JOIN `tabAI Lead` al ON al.name = h.lead
        WHERE h.lead IS NOT NULL
            AND h.lead != ''
            AND al.name IS NULL
            AND IFNULL(h.status, '') != 'Closed'
        """,
        as_dict=True,
    )

    closed = 0

    for row in rows:
        note = "Closed by stabilization patch: referenced AI Lead no longer exists."
        existing_notes = frappe.db.get_value(
            "AI Handoff",
            row.name,
            "notes",
        ) or ""
        notes = (
            f"{existing_notes}\n\n{note}".strip()
            if existing_notes
            else note
        )
        frappe.db.set_value(
            "AI Handoff",
            row.name,
            {
                "status": "Closed",
                "notes": notes,
            },
            update_modified=False,
        )
        _close_related_todos(row.name)
        closed += 1

    frappe.db.commit()
    frappe.logger().info(
        f"cleanup_orphan_handoffs closed={closed}"
    )


def _close_related_todos(handoff_name):
    todos = frappe.get_all(
        "ToDo",
        filters={
            "reference_type": "AI Handoff",
            "reference_name": handoff_name,
        },
        pluck="name",
    )

    for todo in todos:
        if frappe.db.has_column("ToDo", "status"):
            frappe.db.set_value(
                "ToDo",
                todo,
                "status",
                "Closed",
                update_modified=False,
            )

        if frappe.db.has_column("ToDo", "completed"):
            frappe.db.set_value(
                "ToDo",
                todo,
                "completed",
                1,
                update_modified=False,
            )
