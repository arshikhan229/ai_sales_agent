import frappe


def get_sales_users():

    users = frappe.get_all(
        "User",
        filters={
            "enabled": 1,
            "user_type": "System User"
        },
        fields=["name"],
        order_by="creation asc"
    )

    result = []

    for user in users:

        if user.name in (
            "Administrator",
            "Guest"
        ):
            continue

        result.append(
            user.name
        )

    return result


def get_last_assigned_user():

    rows = frappe.get_all(
        "AI Handoff",
        fields=["assigned_to"],
        order_by="creation desc",
        limit=1
    )

    if rows:
        return rows[0].assigned_to

    return None


def get_round_robin_user():

    users = get_sales_users()

    if not users:
        return "Administrator"

    last_user = get_last_assigned_user()

    if not last_user:
        return users[0]

    if last_user not in users:
        return users[0]

    index = users.index(
        last_user
    )

    next_index = (
        index + 1
    ) % len(users)

    return users[
        next_index
    ]


def assign_lead(
    ai_lead=None,
    opportunity=None
):

    user = get_round_robin_user()

    if opportunity:

        try:

            frappe.share.add(
                "Opportunity",
                opportunity,
                user=user,
                write=1,
                share=1,
                notify=0
            )

        except Exception:
            pass

    return user
