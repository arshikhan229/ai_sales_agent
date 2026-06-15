import frappe
from .inbox_service import get_unified_conversations


@frappe.whitelist()
def get_inbox():
    """API wrapper returning unified inbox conversations."""
    try:
        conv = get_unified_conversations()
        return {"conversations": conv}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "unified_inbox_api_error")
        return {"conversations": [], "error": "exception"}
