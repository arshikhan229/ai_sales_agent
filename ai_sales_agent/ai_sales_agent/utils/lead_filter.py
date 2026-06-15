BLOCKED_SENDER_PATTERNS = (
    "noreply@",
    "no-reply@",
    "no_reply@",
    "donotreply@",
    "do-not-reply@",
    "notifications@",
    "notification@",
    "updates@",
    "support@",
    "mailer-daemon@",
)

BLOCKED_DOMAINS = (
    "github.com",
    "substack.com",
    "academia-mail.com",
    "linkedin.com",
    "economist.com",
    "temuemail.com",
    "coursera.org",
    "render.com",
    "incident.io",
)

BLOCKED_SUBJECT_KEYWORDS = (
    "newsletter",
    "weekly digest",
    "digest",
    "unsubscribe",
    "ci failed",
    "workflow run",
    "final reminder",
    "daily digest",
    "coursera",
    "quora",
    "substack",
    "temu",
    "notification",
)

BLOCKED_CONTENT_KEYWORDS = (
    "newsletter",
    "digest",
    "unsubscribe",
    "list-unsubscribe",
    "manage notifications",
    "view in browser",
    "coursera",
    "quora digest",
    "substack",
    "temu",
)

SALES_KEYWORDS = (
    "erp",
    "erpnext",
    "quotation",
    "quote",
    "pricing",
    "price",
    "demo",
    "implementation",
    "consulting",
    "inventory",
    "procurement",
    "purchase",
    "crm",
    "automation",
    "integration",
    "software",
)


def has_sales_intent(subject, content):

    text = f"{subject} {content}".lower()

    return any(
        keyword in text
        for keyword in SALES_KEYWORDS
    )


def should_process_email(
    sender,
    subject,
    content,
    headers=None,
):

    sender = (sender or "").lower().strip()
    subject = (subject or "").lower()
    content = (content or "").lower()
    header_text = _normalize_headers(headers)

    if "list-unsubscribe" in header_text:
        return {
            "process": False,
            "reason": "list_unsubscribe",
        }

    # Block sender patterns
    for pattern in BLOCKED_SENDER_PATTERNS:

        if pattern in sender:

            return {
                "process": False,
                "reason": "system_sender",
            }

    # Block domains
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

    # Block subjects
    for keyword in BLOCKED_SUBJECT_KEYWORDS:

        if keyword in subject:

            return {
                "process": False,
                "reason": "newsletter",
            }

    # Block content
    for keyword in BLOCKED_CONTENT_KEYWORDS:

        if keyword in content:

            return {
                "process": False,
                "reason": "marketing_content",
            }

    # MUST contain sales intent
    if not has_sales_intent(
        subject,
        content
    ):

        return {
            "process": False,
            "reason": "no_sales_intent",
        }

    return {
        "process": True,
        "reason": None,
    }


def _normalize_headers(headers):
    if not headers:
        return ""

    if isinstance(headers, dict):
        return "\n".join(
            f"{key}: {value}"
            for key, value in headers.items()
        ).lower()

    return str(headers).lower()
