import frappe


def execute():
    if not frappe.db.table_exists("AI Handoff"):
        return

    rows = frappe.db.sql(
        """
        SELECT h.name, h.notes
        FROM `tabAI Handoff` h
        LEFT JOIN `tabAI Lead` al ON al.name = h.lead
        WHERE h.lead IS NOT NULL
            AND h.lead != ''
            AND al.name IS NULL
        """,
        as_dict=True,
    )

    cleared = 0

    for row in rows:
        note = "Cleared orphan AI Lead link by stabilization patch."
        notes = row.notes or ""

        if note not in notes:
            notes = (
                f"{notes}\n\n{note}".strip()
                if notes
                else note
            )

        frappe.db.set_value(
            "AI Handoff",
            row.name,
            {
                "lead": None,
                "status": "Closed",
                "notes": notes,
            },
            update_modified=False,
        )
        cleared += 1

    frappe.db.commit()
    frappe.logger().info(
        f"clear_orphan_handoff_links cleared={cleared}"
    )
