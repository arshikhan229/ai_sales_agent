import frappe
from .inbox_service import get_unified_conversations


@frappe.whitelist()
def get_inbox():
    """API wrapper returning unified inbox conversations."""

    try:

        conversations = get_unified_conversations()

        for row in conversations:

            ai_lead = None

            contact = (
                row.get("contact")
                or ""
            )

            if contact:

                ai_lead = frappe.db.get_value(
                    "AI Lead",
                    {
                        "custom_phone": contact
                    },
                    "name"
                )

                if not ai_lead:

                    ai_lead = frappe.db.get_value(
                        "AI Lead",
                        {
                            "lead_name": contact
                        },
                        "name"
                    )

            row["ai_lead"] = ai_lead

        return {
            "conversations": conversations
        }

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "unified_inbox_api_error"
        )

        return {
            "conversations": [],
            "error": "exception"
        }