import frappe
from ai_sales_agent.ai_sales_agent.utils import communication_processor, followup_tracker


def communication_after_insert(doc, method):
    """Wrapper to run main communication processing and follow-up tracking."""
    try:
        # main processing (existing behavior)
        try:
            communication_processor.process_communication(doc, method)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "communication_processor_error")

        # follow-up tracking
        try:
            followup_tracker.on_communication(doc, method)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "followup_tracker_on_communication_error")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "communication_after_insert_error")
