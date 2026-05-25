import frappe


def find_duplicate_lead(email=None):
    """
    Check if lead already exists using email
    """

    if not email:
        return None

    existing = frappe.db.exists(
        "AI Lead",
        {
            "email": email
        }
    )

    return existing