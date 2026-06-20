frappe.pages['handoff-workspace'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Handoff Workspace',
        single_column: true
    });

    page.body.html(`
        <div id="handoff-workspace-content">
            Select a handoff...
        </div>
    `);

    let route = frappe.get_route();

    if (route.length > 1) {

        let handoff = route[1];

        if (handoff) {

            setTimeout(() => {
                load_handoff(handoff);
            }, 500);
        }
    }

    function load_handoff(handoff) {

        frappe.call({
            method:
                "ai_sales_agent.ai_sales_agent.page.handoff_workspace.handoff_workspace.get_handoff_workspace",

            args: {
                handoff: handoff
            },

            callback: function(r) {

                let data = r.message;

                if (!data) {

                    frappe.msgprint(
                        "Handoff not found"
                    );

                    return;
                }

                let h = data.handoff;

                let conversations_html = "";

                (data.conversations || []).forEach(row => {

                    conversations_html += `
                        <tr>
                            <td>${row.channel || ""}</td>
                            <td>${row.direction || ""}</td>
                            <td>${row.message || ""}</td>
                            <td>${row.timestamp || ""}</td>
                        </tr>
                    `;
                });

                let todos_html = "";

                (data.todos || []).forEach(row => {

                    todos_html += `
                        <tr>
                            <td>${row.allocated_to || ""}</td>
                            <td>${row.status || ""}</td>
                            <td>${row.creation || ""}</td>
                        </tr>
                    `;
                });

                $("#handoff-workspace-content").html(`

                    <div class="card p-4 mb-3">

                        <h3>${h.name}</h3>

                        <p><b>Lead:</b> ${h.lead || ""}</p>

                        <p><b>Assigned To:</b> ${h.assigned_to || ""}</p>

                        <p><b>Status:</b> ${h.status || ""}</p>

                        <p><b>Priority:</b> ${h.priority || ""}</p>

                        <p><b>Opportunity:</b> ${h.opportunity || ""}</p>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>AI Recommendations</h4>

                        <p>
                            <b>Next Best Action:</b>
                            ${h.next_best_action || ""}
                        </p>

                        <p>
                            <b>Suggested Reply:</b>
                            ${h.ai_suggested_reply || ""}
                        </p>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>Follow-up Status</h4>

                        <p>
                            <b>Followups:</b>
                            ${h.followup_count || 0}
                        </p>

                        <p>
                            <b>Last Followup:</b>
                            ${h.last_followup_at || ""}
                        </p>

                        <p>
                            <b>Next Followup:</b>
                            ${h.next_followup_due || ""}
                        </p>

                        <p>
                            <b>SLA:</b>
                            ${h.sla_status || ""}
                        </p>

                    </div>

                    <div class="card p-4 mb-3">

                        <h4>Conversation History</h4>

                        <table class="table table-bordered">

                            <thead>
                                <tr>
                                    <th>Channel</th>
                                    <th>Direction</th>
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

                        <h4>Follow-up Tasks</h4>

                        <table class="table table-bordered">

                            <thead>
                                <tr>
                                    <th>Assigned To</th>
                                    <th>Status</th>
                                    <th>Created</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${todos_html}
                            </tbody>

                        </table>

                    </div>

                `);
            }
        });
    }
};