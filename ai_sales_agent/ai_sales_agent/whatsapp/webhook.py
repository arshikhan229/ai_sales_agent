import frappe
from werkzeug.wrappers import Response

from ai_sales_agent.ai_sales_agent.utils.channel_processor import (
    process_inbound_message,
)
from ai_sales_agent.ai_sales_agent.utils.webhook_security import (
    validate_twilio_request,
)


@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():

    try:

        if not validate_twilio_request():
            frappe.log_error(
                "Invalid Twilio webhook signature",
                "WHATSAPP SIGNATURE ERROR",
            )
            return Response(
                response="Forbidden",
                status=403,
            )

        data = frappe.form_dict

        customer_message = (
            data.get("Body")
            or ""
        )

        customer_number = (
            data.get("From")
            or ""
        )

        customer_number = (
            customer_number
            .replace("whatsapp:", "")
            .replace(" ", "")
            .strip()
        )

        if customer_number and not customer_number.startswith("+"):
            customer_number = f"+{customer_number}"

        frappe.logger().info(
            f"WHATSAPP INCOMING => {customer_number} : {customer_message}"
        )

        if not customer_number:

            frappe.log_error(
                "EMPTY CUSTOMER NUMBER",
                "WHATSAPP ERROR"
            )

            return "OK"

        result = process_inbound_message(
            channel="WhatsApp",
            message=customer_message,
            phone=customer_number,
            reply_target={
                "phone": customer_number,
            },
        )

        if result.get("success"):

            frappe.logger().info(
                "WHATSAPP FLOW SUCCESS"
            )

            return "OK"

        if result.get("skipped"):

            return "OK"

        frappe.log_error(
            frappe.as_json(result),
            "WHATSAPP PROCESSOR FAILED",
        )

        return "ERROR"

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "WHATSAPP WEBHOOK ERROR"
        )

        return "ERROR"
