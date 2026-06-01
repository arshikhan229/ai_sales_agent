VALID_INTENTS = [
    "Pricing Inquiry",
    "Product Inquiry",
    "Support Request",
    "Demo Request",
    "Billing Inquiry",
    "Complaint",
    "Partnership Inquiry",
    "General Inquiry"
]


def detect_intent(message=""):

    message = (message or "").lower()

    pricing_keywords = [
        "price",
        "pricing",
        "cost",
        "quotation",
        "quote"
    ]

    demo_keywords = [
        "demo",
        "meeting",
        "presentation"
    ]

    support_keywords = [
        "issue",
        "error",
        "problem",
        "bug",
        "help",
        "support"
    ]

    billing_keywords = [
        "invoice",
        "payment",
        "refund",
        "billing"
    ]

    partnership_keywords = [
        "partner",
        "partnership",
        "reseller",
        "collaboration"
    ]

    complaint_keywords = [
        "complaint",
        "unhappy",
        "bad service"
    ]

    for word in pricing_keywords:
        if word in message:
            return "Pricing Inquiry"

    for word in demo_keywords:
        if word in message:
            return "Demo Request"

    for word in support_keywords:
        if word in message:
            return "Support Request"

    for word in billing_keywords:
        if word in message:
            return "Billing Inquiry"

    for word in partnership_keywords:
        if word in message:
            return "Partnership Inquiry"

    for word in complaint_keywords:
        if word in message:
            return "Complaint"

    return "General Inquiry"