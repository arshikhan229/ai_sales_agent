frappe.pages['customer-profile'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Customer Profile',
        single_column: true
    });

    page.body.html(`
        <div id="customer-profile-content" class="mt-3">
            Select a customer...
        </div>
    `);

    let route = frappe.get_route();

    if (route.length > 1) {

        let ai_lead = route[1];

        if (ai_lead) {
            setTimeout(() => {
                load_profile(ai_lead);
            }, 500);
        }
    }

    page.set_primary_action(
        "Load Customer",
        () => {

            frappe.prompt(
                [{
                    fieldname: "ai_lead",
                    label: "AI Lead",
                    fieldtype: "Link",
                    options: "AI Lead",
                    reqd: 1
                }],
                function(values) {

                    load_profile(values.ai_lead);

                },
                "Load Customer",
                "Load"
            );

        }
    );

    function load_profile(ai_lead) {

        frappe.call({
            method:
                "ai_sales_agent.ai_sales_agent.page.customer_profile.customer_profile.get_customer_profile_data",

            args: {
                ai_lead: ai_lead
            },

            callback: function(r) {

                let p = r.message;

                if (!p) {
                    frappe.msgprint("Profile not found");
                    return;
                }

                let conversations_html = "";

                (p.conversations || []).forEach(row => {

                    conversations_html += `
                        <tr>
                            <td>${row.channel || ""}</td>
                            <td>${row.message || ""}</td>
                            <td>${row.timestamp || ""}</td>
                        </tr>
                    `;
                });

                let handoffs_html = "";

                (p.handoffs || []).forEach(row => {

                    handoffs_html += `
                        <tr>
                            <td>${row.assigned_to || ""}</td>

                            <td>
                                <a href="/app/handoff-workspace/${row.name}">
                                    ${row.status || ""}
                                </a>
                            </td>

                            <td>${row.opportunity || ""}</td>
                        </tr>
                    `;
                });

                $("#customer-profile-content").html(`

                    <div class="card p-4 mb-3">

                        <h3>${p.lead.lead_name || ""}</h3>

                        <p>
                            <b>Category:</b>
                            ${p.lead.category || ""}
                        </p>

                        <p>
                            <b>Phone:</b>
                            ${p.lead.phone || ""}
                        </p>

                        <p>
                            <b>Email:</b>
                            ${p.lead.email || ""}
                        </p>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>ERPNext CRM</h4>

                        <p>

                            <b>ERP Lead:</b>

                            ${p.lead.erp_lead || ""}

                            ${
                                p.lead.erp_lead
                                ?
                                `
                                <button
                                    class="btn btn-sm btn-primary open-lead"
                                    data-lead="${p.lead.erp_lead}"
                                >
                                    Open Lead
                                </button>
                                `
                                :
                                ""
                            }

                        </p>

                        <p>

                            <b>Opportunity:</b>

                            ${p.lead.opportunity || ""}

                            ${
                                p.lead.opportunity
                                ?
                                `
                                <button
                                    class="btn btn-sm btn-success open-opportunity"
                                    data-opportunity="${p.lead.opportunity}"
                                >
                                    Open Opportunity
                                </button>
                                `
                                :
                                ""
                            }

                        </p>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>Conversations</h4>

                        <table class="table table-bordered">

                            <thead>
                                <tr>
                                    <th>Channel</th>
                                    <th>Message</th>
                                    <th>Timestamp</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${conversations_html}
                            </tbody>

                        </table>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>Handoffs</h4>

                        <table class="table table-bordered">

                            <thead>
                                <tr>
                                    <th>Assigned To</th>
                                    <th>Status</th>
                                    <th>Opportunity</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${handoffs_html}
                            </tbody>

                        </table>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>Omnichannel Timeline</h4>

                        <div id="customer-timeline">
                            Loading timeline...
                        </div>

                    </div>

                `);

                load_timeline(ai_lead);

                $(document)
                    .off("click", ".open-lead")
                    .on("click", ".open-lead", function() {

                        frappe.set_route(
                            "Form",
                            "Lead",
                            $(this).data("lead")
                        );

                    });

                $(document)
                    .off("click", ".open-opportunity")
                    .on("click", ".open-opportunity", function() {

                        frappe.set_route(
                            "Form",
                            "Opportunity",
                            $(this).data("opportunity")
                        );

                    });
            }
        });
    }

    function load_timeline(ai_lead) {

        frappe.call({
            method:
                "ai_sales_agent.ai_sales_agent.page.customer_profile.customer_profile.get_omnichannel_timeline",

            args: {
                ai_lead: ai_lead
            },

            callback: function(r) {

                let rows = r.message || [];

                if (!rows.length) {

                    $("#customer-timeline").html(
                        "<p>No timeline events found.</p>"
                    );

                    return;
                }

                let html = "";

                rows.forEach(row => {

                    html += `

                        <div
                            style="
                                border-left:4px solid #5e64ff;
                                padding-left:15px;
                                margin-bottom:20px;
                            "
                        >

                            <div>

                                <span class="badge badge-primary">
                                    ${row.type || ""}
                                </span>

                            </div>

                            <div style="margin-top:5px;">

                                <strong>
                                    ${row.title || ""}
                                </strong>

                            </div>

                            ${
                                row.status
                                ?
                                `
                                <div>
                                    Status:
                                    ${row.status}
                                </div>
                                `
                                :
                                ""
                            }

                            <div>

                                <small>
                                    ${row.timestamp || ""}
                                </small>

                            </div>

                        </div>

                    `;
                });

                $("#customer-timeline").html(
                    html
                );
            }
        });
    }
};