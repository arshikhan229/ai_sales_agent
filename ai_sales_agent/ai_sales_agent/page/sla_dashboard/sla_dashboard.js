frappe.pages['sla-dashboard'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SLA Dashboard',
        single_column: true
    });

    page.body.html(`
        <div id="sla-summary"></div>
        <div id="sla-table"></div>
    `);

    function load_dashboard() {

        frappe.call({
            method:
                "ai_sales_agent.ai_sales_agent.page.sla_dashboard.sla_dashboard.get_sla_dashboard",

            callback: function(r) {

                let data = r.message || {};

                let s = data.summary || {};

                $("#sla-summary").html(`
                    <div style="display:flex;gap:20px;margin-bottom:20px;">
                        <div class="card p-3">
                            <h4>Total Handoffs</h4>
                            <h2>${s.total || 0}</h2>
                        </div>

                        <div class="card p-3">
                            <h4>SLA Breaches</h4>
                            <h2>${s.breached || 0}</h2>
                        </div>

                        <div class="card p-3">
                            <h4>Overdue</h4>
                            <h2>${s.overdue || 0}</h2>
                        </div>
                    </div>
                `);

                let html = `
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Lead</th>
                                <th>Assigned</th>
                                <th>Status</th>
                                <th>Days Open</th>
                                <th>Followups</th>
                                <th>Next Followup</th>
                                <th>SLA</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                (data.handoffs || []).forEach(row => {

                    html += `
                        <tr>
                            <td>${row.lead || ""}</td>
                            <td>${row.assigned_to || ""}</td>
                            <td>${row.status || ""}</td>
                            <td>${row.days_open || 0}</td>
                            <td>${row.followup_count || 0}</td>
                            <td>${row.next_followup_due || ""}</td>
                            <td>${row.sla_status || ""}</td>
                        </tr>
                    `;
                });

                html += `
                        </tbody>
                    </table>
                `;

                $("#sla-table").html(html);
            }
        });
    }

    load_dashboard();

    page.set_primary_action(
        "Refresh",
        () => load_dashboard()
    );
};