def get_route_department(intent):
    """
    Route lead based on intent
    """

    mapping = {

        "Pricing Inquiry": "Sales",

        "Product Inquiry": "Sales",

        "Demo Request": "Sales",

        "Support Request": "Support",

        "Billing Inquiry": "Accounts",

        "Complaint": "Management",

        "Partnership Inquiry": "Business Development",

        "General Inquiry": "General"
    }

    return mapping.get(intent, "General")