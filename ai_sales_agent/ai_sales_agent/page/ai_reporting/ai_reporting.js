frappe.pages['ai-reporting'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI Reporting',
        single_column: true
    });

    // Top KPIs
    let kpi_area = $('<div>').appendTo(page.body);
    kpi_area.html('<div id="kpi_cards" style="display:flex;gap:12px;margin-bottom:18px;flex-wrap:wrap"></div>');

    // Charts
    let chart_area = $('<div>').appendTo(page.body);
    chart_area.html('\
        <div class="row">\
            <div class="col-md-6"><div id="funnel_chart"></div></div>\
            <div class="col-md-6"><div id="channel_chart"></div></div>\
        </div>\
        <div class="row" style="margin-top:18px;">\
            <div class="col-md-6"><div id="agent_chart"></div></div>\
            <div class="col-md-6"><div id="sla_chart"></div></div>\
        </div>');

    function render_kpis(data) {
        let cards = $('#kpi_cards');
        cards.empty();
        const kpis = [
            ['Total Leads', data.total_leads],
            ['Qualified', data.qualified_leads || data.qualified || 0],
            ['Hot Leads', data.hot_leads || 0],
            ['Opportunities', data.opportunities || 0],
            ['Won', data.opportunities_won || data.won || 0],
            ['Pipeline', data.pipeline_value || 0],
            ['Conversion %', (data.conversion_rate || 0).toFixed(2)],
            ['Open Handoffs', data.open_handoffs || 0]
        ];

        kpis.forEach(k => {
            let c = $('<div class="card" style="padding:10px;min-width:160px;"></div>');
            c.html('<div style="font-size:12px;color:#666">'+k[0]+'</div><div style="font-size:18px;font-weight:700">'+k[1]+'</div>');
            cards.append(c);
        });
    }

    function load_all() {
        frappe.call({
            method: 'ai_sales_agent.ai_sales_agent.reporting.reporting.get_dashboard_metrics',
            callback: function(r) {
                if (r.message) render_kpis(r.message);
            }
        });

        frappe.call({
            method: 'ai_sales_agent.ai_sales_agent.reporting.reporting.get_funnel_metrics',
            callback: function(r) {
                if (r.message) {
                    const ds = r.message;
                    // simple funnel using frappe.Chart
                    try {
                        new frappe.Chart('#funnel_chart', {
                            data: {
                                labels: ['Leads','Qualified','Opportunity','Won'],
                                datasets: [{name: 'Funnel', values: [ds.lead, ds.qualified, ds.opportunity, ds.won]}]
                            },
                            type: 'bar',
                            height: 250
                        });
                    } catch(e) {}
                }
            }
        });

        frappe.call({
            method: 'ai_sales_agent.ai_sales_agent.reporting.reporting.get_channel_metrics',
            callback: function(r) {
                if (r.message) {
                    const d = r.message;
                    try {
                        new frappe.Chart('#channel_chart', {
                            data: {
                                labels: ['WhatsApp','Facebook','Email'],
                                datasets: [{name: 'Leads', values: [d.whatsapp_leads, d.facebook_leads, d.email_leads]}]
                            },
                            type: 'pie',
                            height: 250
                        });
                    } catch(e) {}
                }
            }
        });

        frappe.call({
            method: 'ai_sales_agent.ai_sales_agent.reporting.reporting.get_agent_metrics',
            callback: function(r) {
                if (r.message && r.message.length) {
                    const rows = r.message;
                    const labels = rows.map(x => x.agent || 'Unassigned');
                    const vals = rows.map(x => x.assigned_leads || 0);
                    try {
                        new frappe.Chart('#agent_chart', {
                            data: {labels: labels, datasets: [{name: 'Assigned Leads', values: vals}]},
                            type: 'bar',
                            height: 250
                        });
                    } catch(e) {}
                }
            }
        });

        frappe.call({
            method: 'ai_sales_agent.ai_sales_agent.reporting.reporting.get_sla_metrics',
            callback: function(r) {
                if (r.message) {
                    const keys = Object.keys(r.message || {});
                    const vals = keys.map(k => r.message[k]);
                    try {
                        new frappe.Chart('#sla_chart', {
                            data: {labels: keys, datasets: [{name: 'SLA', values: vals}]},
                            type: 'donut',
                            height: 250
                        });
                    } catch(e) {}
                }
            }
        });
    }

    load_all();

    page.set_primary_action('Refresh', () => load_all());
};
