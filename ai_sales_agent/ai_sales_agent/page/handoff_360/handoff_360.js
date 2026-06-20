frappe.pages['handoff-360'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Handoff 360',
        single_column: true
    });

    let route = frappe.get_route();

    let handoff = route[1];

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.handoff_360.handoff_360.get_handoff_360",

        args: {
            handoff: handoff
        },

        callback: function(r) {

            let d = r.message || {};

            page.body.html(`

                <div class="card p-4">

                    <h2>${d.name}</h2>

                    <hr>

                    <div class="row">

                        <div class="col-md-6">

                            <p><b>Assigned To:</b> ${d.assigned_to || ""}</p>

                            <p><b>Status:</b> ${d.status || ""}</p>

                            <p><b>Priority:</b> ${d.priority || ""}</p>

                            <p><b>Channel:</b> ${d.channel || ""}</p>

                            <p><b>Lead:</b> ${d.lead || ""}</p>

                            <p><b>Contact:</b> ${d.contact || ""}</p>

                        </div>

                        <div class="col-md-6">

                            <p><b>Opportunity:</b> ${d.opportunity || ""}</p>

                            <p><b>SLA:</b> ${d.sla_status || ""}</p>

                            <p><b>Days Open:</b> ${d.days_open || 0}</p>

                            <p><b>Followups:</b> ${d.followup_count || 0}</p>

                            <p><b>Next Followup:</b> ${d.next_followup_due || ""}</p>

                            <p><b>Created:</b> ${d.creation || ""}</p>

                        </div>

                    </div>

                </div>

                <br>

                <div class="card p-4">

                    <h3>AI Intelligence</h3>

                    <hr>

                    <p>

                        <b>Intent:</b>

                        ${d.created_from_intent || ""}

                    </p>

                    <p>

                        <b>Category:</b>

                        ${d.created_from_category || ""}

                    </p>

                    <p>

                        <b>Next Best Action:</b>

                        ${d.next_best_action || ""}

                    </p>

                    <p>

                        <b>AI Suggested Reply:</b>

                    </p>

                    <div class="alert alert-info">

                        ${d.ai_suggested_reply || ""}

                    </div>

                </div>

                <br>

                <div class="card p-4">

                    <h3>Notes</h3>

                    <hr>

                    <p>

                        ${d.notes || "No notes available"}

                    </p>

                </div>

                <br>

                <div>

                    <button
                        class="btn btn-primary open-opportunity"
                        data-name="${d.opportunity || ''}"
                    >
                        Open Opportunity 360
                    </button>

                </div>

            `);

        }

    });

};


$(document).on(
    "click",
    ".open-opportunity",
    function() {

        let opp =
            $(this).data("name");

        if(!opp) {
            frappe.msgprint(
                "No opportunity linked."
            );
            return;
        }

        frappe.set_route(
            "opportunity-360",
            opp
        );

    }
);