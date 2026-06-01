import frappe


def find_or_create_contact(
    email=None,
    phone=None,
    facebook_id=None,
    instagram_id=None,
    linkedin_id=None,
    company=None
):

    # Facebook Match
    if facebook_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_facebook_id": facebook_id
            }
        )

        if contact_name:
            return frappe.get_doc(
                "Contact",
                contact_name
            )

    # Instagram Match
    if instagram_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_instagram_id": instagram_id
            }
        )

        if contact_name:
            return frappe.get_doc(
                "Contact",
                contact_name
            )

    # LinkedIn Match
    if linkedin_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_linkedin_id": linkedin_id
            }
        )

        if contact_name:
            return frappe.get_doc(
                "Contact",
                contact_name
            )

    # Email Match
    if email:

        email_parent = frappe.db.get_value(
            "Contact Email",
            {
                "email_id": email
            },
            "parent"
        )

        if email_parent:
            return frappe.get_doc(
                "Contact",
                email_parent
            )

    # Phone Match
    if phone:

        phone_parent = frappe.db.get_value(
            "Contact Phone",
            {
                "phone": phone
            },
            "parent"
        )

        if phone_parent:
            return frappe.get_doc(
                "Contact",
                phone_parent
            )

    # Create Contact

    source = "Manual"

    if facebook_id:
        source = "Facebook"

    elif instagram_id:
        source = "Instagram"

    elif linkedin_id:
        source = "LinkedIn"

    elif email:
        source = "Email"

    contact_name = (
        f"FB_{facebook_id}"
        if facebook_id
        else "Customer"
    )

    contact = frappe.get_doc({
        "doctype": "Contact",

        "first_name": contact_name,

        "company_name": company,

        "custom_facebook_id":
            facebook_id,

        "custom_instagram_id":
            instagram_id,

        "custom_linkedin_id":
            linkedin_id,

        "custom_source_first":
            source,

        "custom_lead_score":
            0,

        "custom_lead_category":
            "Cold"
    })

    if email:

        contact.append(
            "email_ids",
            {
                "email_id": email,
                "is_primary": 1
            }
        )

    if phone:

        contact.append(
            "phone_nos",
            {
                "phone": phone,
                "is_primary_mobile_no": 1
            }
        )

    contact.insert(
        ignore_permissions=True
    )

    frappe.db.commit()

    return contact