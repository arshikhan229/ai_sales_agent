frappe.pages['supervisor-queue'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Supervisor Queue',
        single_column: true
    });

    page.body.html(`
        <div id="supervisor-queue-container">
            Loading...
        </div>
    `);

    function load_queue() {

        frappe.call({
            method:
                "ai_sales_agent.ai_sales_agent.page.supervisor_queue.supervisor_queue.get_handoffs",

            callback: function(r) {

                const rows =
                    r.message || [];

                let html = `
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Handoff</th>
                                <th>Lead</th>
                                <th>Assigned To</th>
                                <th>Status</th>
                                <th>Priority</th>
                                <th>Opportunity</th>
                                <th>Followups</th>
                                <th>SLA</th>
                                <th>Next Action</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                rows.forEach(row => {

                    html += `
                        <tr>
                            <td>${row.name || ""}</td>
                            <td>${row.lead || ""}</td>
                            <td>${row.assigned_to || ""}</td>
                            <td>${row.status || ""}</td>
                            <td>${row.priority || ""}</td>
                            <td>${row.opportunity || ""}</td>
                            <td>${row.followup_count || 0}</td>
                            <td>${row.sla_status || ""}</td>
                            <td>${row.next_best_action || ""}</td>
                        </tr>
                    `;
                });

                html += `
                        </tbody>
                    </table>
                `;

                $("#supervisor-queue-container")
                    .html(html);
            }
        });
    }

    load_queue();

    page.set_primary_action(
        "Refresh",
        () => load_queue()
    );
};