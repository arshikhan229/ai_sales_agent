frappe.pages['activity-feed'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Activity Feed',
        single_column: true
    });

    page.set_primary_action(
        "Refresh",
        () => load_feed()
    );

    page.body.html(`
        <div id="activity-feed-container"></div>
    `);

    load_feed();

    function load_feed() {

        frappe.call({
            method:
            "ai_sales_agent.ai_sales_agent.page.activity_feed.activity_feed.get_activity_feed",

            callback: function(r) {

                render_feed(
                    r.message || []
                );
            }
        });
    }

    function render_feed(rows) {

        let html = "";

        rows.forEach(row => {

            html += `

                <div
                    class="card"
                    style="
                        margin-bottom:12px;
                        padding:15px;
                        border-left:5px solid #5e64ff;
                    "
                >

                    <div>

                        <span class="badge badge-primary">
                            ${row.type}
                        </span>

                    </div>

                    <div style="margin-top:8px;">

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

        $("#activity-feed-container").html(
            html
        );
    }
};