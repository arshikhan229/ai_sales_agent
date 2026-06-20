frappe.pages['sales-manager'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI Sales Manager Dashboard',
        single_column: true
    });

    page.set_primary_action(
        "Refresh",
        () => load_dashboard()
    );

    page.body.html(`
        <div id="sales-kpis"
             style="
                display:flex;
                gap:15px;
                flex-wrap:wrap;
             ">
        </div>
    `);

    load_dashboard();

    function load_dashboard() {

        frappe.call({
            method:
            "ai_sales_agent.ai_sales_agent.page.sales_manager.sales_manager.get_dashboard_data",

            callback: function(r) {

                render_kpis(
                    r.message || {}
                );
            }
        });
    }

    function render_kpis(data) {

        let cards = [

            ["Total Leads", data.total_leads],
            ["Hot Leads", data.hot_leads],
            ["Open Opportunities", data.open_opportunities],
            ["Closed Opportunities", data.closed_opportunities],
            ["Open Handoffs", data.open_handoffs],
            ["Followups Due", data.followups_due],
            ["Pipeline Value", data.pipeline_value]

        ];

        let html = "";

        cards.forEach(card => {

            html += `
                <div
                    class="card"
                    style="
                        width:220px;
                        padding:20px;
                    "
                >

                    <div
                        style="
                            font-size:14px;
                            color:#666;
                        "
                    >
                        ${card[0]}
                    </div>

                    <div
                        style="
                            font-size:28px;
                            font-weight:bold;
                            margin-top:10px;
                        "
                    >
                        ${card[1] || 0}
                    </div>

                </div>
            `;
        });

        $("#sales-kpis").html(html);
    }
};