import frappe
def find_or_create_contact(
    email=None,
    phone=None,
    facebook_id=None,
    instagram_id=None,
    linkedin_id=None,
    company=None
):

    # =================================
    # NORMALIZE PHONE
    # =================================

    if phone:

        phone = (
            phone
            .replace(" ", "")
            .strip()
        )

        if not phone.startswith("+"):
            phone = f"+{phone}"

    # =================================
    # FACEBOOK MATCH
    # =================================

    if facebook_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_facebook_id": facebook_id
            }
        )

        if contact_name:

            contact = frappe.get_doc(
                "Contact",
                contact_name
            )

            if email and not contact.email_id:

                contact.email_id = email

                contact.save(
                    ignore_permissions=True
                )

            if phone and not contact.mobile_no:

                contact.mobile_no = phone

                contact.save(
                    ignore_permissions=True
                )

            return contact

    # =================================
    # INSTAGRAM MATCH
    # =================================

    if instagram_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_instagram_id": instagram_id
            }
        )

        if contact_name:

            contact = frappe.get_doc(
                "Contact",
                contact_name
            )

            return contact

    # =================================
    # LINKEDIN MATCH
    # =================================

    if linkedin_id:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "custom_linkedin_id": linkedin_id
            }
        )

        if contact_name:

            contact = frappe.get_doc(
                "Contact",
                contact_name
            )

            return contact

    # =================================
    # PRIMARY EMAIL MATCH
    # =================================

    if email:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "email_id": email
            }
        )

        if contact_name:

            contact = frappe.get_doc(
                "Contact",
                contact_name
            )

            if phone and not contact.mobile_no:

                contact.mobile_no = phone

                contact.save(
                    ignore_permissions=True
                )

            return contact

    # =================================
    # EMAIL CHILD TABLE MATCH
    # =================================

    if email:

        email_parent = frappe.db.get_value(
            "Contact Email",
            {
                "email_id": email
            },
            "parent"
        )

        if email_parent:

            contact = frappe.get_doc(
                "Contact",
                email_parent
            )

            if phone and not contact.mobile_no:

                contact.mobile_no = phone

                contact.save(
                    ignore_permissions=True
                )

            return contact

    # =================================
    # MOBILE MATCH
    # =================================

    if phone:

        contact_name = frappe.db.get_value(
            "Contact",
            {
                "mobile_no": phone
            }
        )

        if contact_name:

            contact = frappe.get_doc(
                "Contact",
                contact_name
            )

            if email and not contact.email_id:

                contact.email_id = email

                contact.save(
                    ignore_permissions=True
                )

            return contact

    # =================================
    # PHONE CHILD TABLE MATCH
    # =================================

    if phone:

        phone_parent = frappe.db.get_value(
            "Contact Phone",
            {
                "phone": phone
            },
            "parent"
        )

        if phone_parent:

            contact = frappe.get_doc(
                "Contact",
                phone_parent
            )

            if email and not contact.email_id:

                contact.email_id = email

                contact.save(
                    ignore_permissions=True
                )

            return contact

    # =================================
    # CREATE NEW CONTACT
    # =================================
    source = "Manual"

    if facebook_id:
        source = "Facebook"

    elif instagram_id:
        source = "Instagram"

    elif linkedin_id:
        source = "LinkedIn"

    elif email:
        source = "Email"

    elif phone:
        source = "WhatsApp"


    contact_name = (
        f"FB_{facebook_id}"
        if facebook_id
        else (
            email.split("@")[0]
            if email
            else (
                phone
                if phone
                else "Customer"
            )
        )
    )

    contact = frappe.get_doc({

        "doctype": "Contact",

        "first_name":
            contact_name,

        "email_id":
            email,

        "mobile_no":
            phone,

        "company_name":
            company,

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