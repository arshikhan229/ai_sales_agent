import frappe


def send_email_reply(
    recipient,
    subject,
    message,
):
    """
    Send email reply
    """

    if not recipient:
        return False

    frappe.sendmail(
        recipients=[recipient],
        subject=f"Re: {subject or 'Your Inquiry'}",
        message=message,
        delayed=False,
    )

    return True