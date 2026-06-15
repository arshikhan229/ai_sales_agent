import frappe


@frappe.whitelist()
def claim_handoff(handoff_name):
    """Assign the AI Handoff to the current user and reassign linked ToDo records.

    Args:
        handoff_name (str): name of the AI Handoff doc

    Returns:
        dict: {status: 'success'|'error', message: str, handoff_name, handoff_status, assigned_to}
    """
    try:
        if not handoff_name:
            return {"status": "error", "message": "handoff_name is required"}

        handoff = frappe.get_doc("AI Handoff", handoff_name)
        user = frappe.session.user

        handoff.assigned_to = user
        if (handoff.status or "").strip().lower() == "open":
            handoff.status = "Assigned"

        handoff.save(ignore_permissions=True)

        for t in _get_related_todos(handoff):
            try:
                td = frappe.get_doc("ToDo", t.name)
                td.allocated_to = user
                td.save(ignore_permissions=True)
            except Exception:
                frappe.log_error(frappe.get_traceback(), "claim_handoff:todo_update_error")

        frappe.db.commit()

        return {
            "status": "success",
            "message": "Handoff claimed",
            "handoff_name": handoff.name,
            "handoff_status": handoff.status,
            "assigned_to": user,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "claim_handoff_error")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def close_handoff(handoff_name, outcome=None, note=None):
    """Close an AI Handoff with an outcome (Closed Won / Closed Lost) and optional note.

    This will:
      - set `status` on the AI Handoff
      - append the note to `notes`
      - mark linked ToDo items as Closed
      - insert a CRM Conversation record with closure event
    """
    try:
        if not handoff_name:
            return {"status": "error", "message": "handoff_name is required"}

        h = frappe.get_doc("AI Handoff", handoff_name)

        outcome = (outcome or "").strip()
        if outcome not in ("Closed Won", "Closed Lost"):
            outcome = "Closed"

        h.status = outcome

        # append closure note
        if note:
            existing = h.get("notes") or ""
            h.notes = (existing + "\n\n[Closed] " + note).strip()

        h.save(ignore_permissions=True)

        # Use direct DB updates to avoid schema differences between installs.
        for t in _get_related_todos(h):
            try:
                # set status column if present
                if _has_todo_column("status"):
                    frappe.db.set_value('ToDo', t.name, 'status', 'Closed')

                # set completed flag if present
                if _has_todo_column("completed"):
                    frappe.db.set_value('ToDo', t.name, 'completed', 1)

            except Exception:
                frappe.log_error(frappe.get_traceback(), "close_handoff:todo_close_error")

        # insert CRM Conversation entry to note the closure
        try:
            conv = frappe.get_doc({
                "doctype": "CRM Conversation",
                "contact": h.contact,
                "channel": h.channel or 'System',
                "direction": "Outgoing",
                "message": f"Handoff closed: {outcome}. {note or ''}",
                "source": "AI Sales Agent",
            })
            conv.insert(ignore_permissions=True)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "close_handoff_conv_error")

        frappe.db.commit()

        return {"status": "success", "message": "Handoff closed", "handoff_name": h.name, "status_value": h.status}

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "close_handoff_error")
        return {"status": "error", "message": str(e)}


def _get_related_todos(handoff):
    filters = [
        [
            "ToDo",
            "reference_type",
            "=",
            "AI Handoff",
        ],
        [
            "ToDo",
            "reference_name",
            "=",
            handoff.name,
        ],
    ]

    todos = {
        todo.name: todo
        for todo in frappe.get_all(
            "ToDo",
            filters=filters,
            fields=["name"],
        )
    }

    if getattr(handoff, "opportunity", None):
        opportunity_todos = frappe.get_all(
            "ToDo",
            filters={
                "reference_type": "Opportunity",
                "reference_name": handoff.opportunity,
            },
            fields=["name"],
        )

        for todo in opportunity_todos:
            todos[todo.name] = todo

    return list(todos.values())


def _has_todo_column(fieldname):
    try:
        return frappe.db.has_column("ToDo", fieldname)
    except Exception:
        return frappe.db.has_column("tabToDo", fieldname)
