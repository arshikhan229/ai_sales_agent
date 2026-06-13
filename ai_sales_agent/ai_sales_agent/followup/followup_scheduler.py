from __future__ import annotations

import frappe

from ai_sales_agent.ai_sales_agent.followup.followup_engine import scan_and_send_followups


def run_daily_followups():
    """Entrypoint for a daily scheduled job (to be added to hooks.py).

    This function is intentionally thin and safe to call multiple times.
    It wraps the engine and logs a summary.
    """
    try:
        frappe.logger().info("Running daily follow-up scheduler")
        summary = scan_and_send_followups()
        frappe.logger().info(f"Follow-up scheduler summary: {summary}")
        return summary
    except Exception:
        frappe.log_error(frappe.get_traceback(), "followup_scheduler_error")
        return {"status": "error"}
