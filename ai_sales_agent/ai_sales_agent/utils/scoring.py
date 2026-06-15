def calculate_icp_score(
    message="",
    email="",
    company=""
):
    score = 0

    message = (message or "").lower()
    email = (email or "").lower()
    company = (company or "").lower()

    # Strong buying signals
    strong_keywords = [
        "pricing",
        "price",
        "cost",
        "quotation",
        "quote",
        "demo",
        "purchase",
        "buy",
        "implementation"
    ]

    # Medium signals
    medium_keywords = [
        "erpnext",
        "crm",
        "software",
        "project",
        "system",
        "solution",
        "requirement",
        "required",
        "automation",
        "platform",
        "integration",
        "implementation",
        "consulting",
        "service"
    ]

    for word in strong_keywords:

        if word in message:
            score += 20

    for word in medium_keywords:

        if word in message:
            score += 15

    free_domains = [
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com"
    ]

    if email and "@" in email:

        domain = email.split("@")[-1]

        if domain not in free_domains:
            score += 10

    if company:
        score += 10

    return min(score, 100)


HOT_BUYING_INTENTS = (
    "Pricing Inquiry",
    "Demo Request",
)

NON_BUYING_INTENTS = (
    "Support Request",
    "Billing Inquiry",
    "Complaint",
)

HOT_BUYING_KEYWORDS = (
    "pricing",
    "price",
    "cost",
    "quotation",
    "quote",
    "proposal",
    "demo",
    "consultation",
    "implementation",
    "erpnext",
)


def has_hot_buying_signal(
    message="",
    intent_type="",
):
    intent_type = intent_type or ""
    message = (message or "").lower()

    if intent_type in HOT_BUYING_INTENTS:
        return True

    if intent_type in NON_BUYING_INTENTS:
        return False

    return any(
        keyword in message
        for keyword in HOT_BUYING_KEYWORDS
    )


def get_lead_category(score):

    if score >= 60:
        return "Hot"

    elif score >= 25:
        return "Warm"

    return "Cold"
