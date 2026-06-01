import frappe

from ai_sales_agent.ai_sales_agent.whatsapp.webhook import (whatsapp_webhook)

@frappe.whitelist(allow_guest=True)
def whatsapp():
    frappe.local.no_csrf = True

    frappe.response["type"] = "json"

    return whatsapp_webhook()
