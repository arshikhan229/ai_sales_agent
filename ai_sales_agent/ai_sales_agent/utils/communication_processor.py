import frappe

from ai_sales_agent.ai_sales_agent.utils.channel_processor import (
    process_inbound_message,
)


def process_communication(doc, method=None):
    """
    Process incoming email communication
    """

    try:

        # Prevent recursion
        if getattr(doc, "_ai_processed", False):
            return

        # =================================
        # EXTRACT EMAIL CONTENT
        # =================================

        content = (
            doc.text_content
            or doc.content
            or doc.subject
            or ""
        )

        sender = (
            doc.sender
            or ""
        )

        subject = (
            doc.subject
            or ""
        )

        headers = (
            getattr(doc, "email_header", None)
            or getattr(doc, "headers", None)
            or getattr(doc, "email_headers", None)
            or ""
        )

        if not content:
            return

        auto_reply = True

        result = process_inbound_message(
            channel="Email",
            message=content,
            email=sender,
            subject=subject,
            headers=headers,
            communication_doc=doc,
            auto_reply=auto_reply,
            reply_target={
                "email": sender,
                "sender": sender,
                "subject": subject
            }
        )

        if result.get("success"):

            frappe.logger().info(
                f"AI ANALYSIS => {result.get('analysis')}"
            )

            frappe.logger().info(
                f"AI REPLY => {result.get('reply')}"
            )

            frappe.logger().info(
                f"AI Communication Processed => {doc.name}"
            )

        elif result.get("skipped"):

            frappe.logger().info(
                f"AI Communication Filtered => {doc.name} : "
                f"{result.get('skip_reason')}"
            )

    except Exception:

        frappe.log_error(
            frappe.get_traceback(),
            "COMMUNICATION PROCESSOR ERROR"
        )
