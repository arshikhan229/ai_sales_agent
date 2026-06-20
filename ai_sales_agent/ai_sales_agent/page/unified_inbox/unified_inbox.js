frappe.pages['unified-inbox'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Unified Inbox',
        single_column: true
    });

    page.body.html(`
        <div id="unified-inbox-container"></div>
    `);

    function loadInbox() {

        frappe.call({
            method: "ai_sales_agent.ai_sales_agent.inbox.inbox_api.get_inbox",
            callback: function(r) {

                const rows =
                    r.message?.conversations || [];

                let html = `
                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th>Channel</th>
                                <th>Contact</th>
                                <th>Lead</th>
                                <th>Last Message</th>
                                <th>Last Activity</th>
                                <th>Priority</th>
                            </tr>
                        </thead>
                        <tbody>
                `;

                rows.forEach(row => {
                    html += `
                        <tr>
                            <td>${row.channel || ""}</td>
                            <td>

                                ${
                                    row.ai_lead
                                    ?
                                    `
                                    <a
                                        href="/app/customer-profile/${row.ai_lead}"
                                    >
                                        ${row.contact || ""}
                                    </a>
                                    `
                                    :
                                    (row.contact || "")
                                }

                            </td>
                            <td>${row.lead || ""}</td>
                            <td>${row.last_message || ""}</td>
                            <td>${row.last_activity || ""}</td>
                            <td>${row.priority || ""}</td>
                        </tr>
                    `;
                });

                html += `
                        </tbody>
                    </table>
                `;

                $("#unified-inbox-container").html(html);
            }
        });
    }

    loadInbox();

    page.set_primary_action(
        "Refresh",
        () => loadInbox()
    );
};