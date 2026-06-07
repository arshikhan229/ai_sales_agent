BLOCKED_SENDER_PATTERNS = (
    "noreply@",
    "no-reply@",
    "notifications@",
    "mailer-daemon@",
)

BLOCKED_DOMAINS = (
    "github.com",
    "substack.com",
    "academia-mail.com",
    "linkedin.com",
)

BLOCKED_SUBJECT_KEYWORDS = (
    "newsletter",
    "weekly digest",
    "unsubscribe",
    "ci failed",
    "workflow run",
)

BLOCKED_CONTENT_KEYWORDS = (
    "unsubscribe",
    "manage notifications",
    "view in browser",
)


def should_process_email(
    sender,
    subject,
    content,
):
    """
    Decide whether an inbound email should enter
    the AI qualification pipeline.

    Returns:
        {"process": True, "reason": None}
        {"process": False, "reason": "<category>"}
    """

    sender = (sender or "").lower().strip()
    subject = (subject or "").lower()
    content = (content or "").lower()

    for pattern in BLOCKED_SENDER_PATTERNS:

        if pattern in sender:

            return {
                "process": False,
                "reason": "system_sender",
            }

    if "@" in sender:

        domain = sender.split("@")[-1]

        for blocked_domain in BLOCKED_DOMAINS:

            if (
                domain == blocked_domain
                or domain.endswith(
                    f".{blocked_domain}"
                )
            ):

                return {
                    "process": False,
                    "reason": "blocked_domain",
                }

    for keyword in BLOCKED_SUBJECT_KEYWORDS:

        if keyword in subject:

            return {
                "process": False,
                "reason": "newsletter",
            }

    for keyword in BLOCKED_CONTENT_KEYWORDS:

        if keyword in content:

            return {
                "process": False,
                "reason": "marketing_content",
            }

    return {
        "process": True,
        "reason": None,
    }
