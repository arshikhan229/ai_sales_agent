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


def normalize_intent(intent):
    """
    Normalize AI-generated intent
    """

    if not intent:
        return "General Inquiry"

    intent = intent.lower()

    mapping = {
        "pricing": "Pricing Inquiry",
        "price": "Pricing Inquiry",
        "quotation": "Pricing Inquiry",

        "product": "Product Inquiry",
        "feature": "Product Inquiry",

        "support": "Support Request",
        "issue": "Support Request",
        "help": "Support Request",

        "demo": "Demo Request",

        "billing": "Billing Inquiry",
        "invoice": "Billing Inquiry",
        "payment": "Billing Inquiry",

        "complaint": "Complaint",

        "partner": "Partnership Inquiry",

        "general": "General Inquiry"
    }

    for keyword, normalized in mapping.items():

        if keyword in intent:
            return normalized

    return "General Inquiry"


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