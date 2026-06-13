import frappe


def execute():
    """Patch to ensure follow-up related fields exist on the AI Settings single doc.

    For existing installations that may not have the new fields, set safe defaults
    so the follow-up engine can run without errors.
    """
    try:
        s = None
        try:
            s = frappe.get_single("AI Settings")
        except Exception:
            # If the single doesn't exist yet, nothing to patch.
            return

        changed = False
        if not hasattr(s, "auto_followup_enabled"):
            try:
                s.set("auto_followup_enabled", False)
                changed = True
            except Exception:
                pass

        if not hasattr(s, "followup_delay_days"):
            try:
                s.set("followup_delay_days", 7)
                changed = True
            except Exception:
                pass

        if not hasattr(s, "max_followup_attempts"):
            try:
                s.set("max_followup_attempts", 3)
                changed = True
            except Exception:
                pass

        if changed:
            try:
                s.save(ignore_permissions=True)
                frappe.db.commit()
            except Exception:
                frappe.log_error(frappe.get_traceback(), "add_followup_settings_save_error")
    except Exception:
        frappe.log_error(frappe.get_traceback(), "add_followup_settings_error")
