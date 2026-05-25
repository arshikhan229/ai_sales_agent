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