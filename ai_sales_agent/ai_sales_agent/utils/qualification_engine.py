def is_sales_qualified(lead):

    if not lead:
        return False

    if lead.intent_type not in [

        "Pricing Inquiry",
        "Demo Request",
        "Product Inquiry",
        "Partnership Inquiry"

    ]:
        return False

    if (lead.icp_score or 0) >= 40:
        return True

    message = (
        lead.message or ""
    ).lower()

    keywords = [

        "price",
        "pricing",
        "quotation",
        "quote",
        "proposal",
        "demo",
        "meeting",
        "implementation",
        "erpnext",
        "users",
        "user",
        "license",
        "licenses"

    ]

    for word in keywords:

        if word in message:
            return True

    return False