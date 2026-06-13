frappe.pages['workforce-dashboard'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Workforce Dashboard',
        single_column: true
    });

    page.body.html('<div id="wf_kpis" style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:12px"></div><div id="wf_charts" class="row"><div class="col-md-6"><div id="leaderboard"></div></div><div class="col-md-6"><div id="agent_bar"></div></div></div>');

    function render_kpis(data) {
        let el = $('#wf_kpis'); el.empty();
        const items = [
            ['Assigned Handoffs', data.total_assigned_handoffs || 0],
            ['Open Opportunities', data.total_open_opportunities || 0],
            ['Follow-ups Due', data.total_followups_due || 0],
            ['SLA Breaches', data.total_sla_breaches || 0]
        ];
        items.forEach(i => {
            el.append('<div class="card" style="padding:10px;min-width:160px"><div style="font-size:12px;color:#666">'+i[0]+'</div><div style="font-size:18px;font-weight:700">'+i[1]+'</div></div>');
        })
    }

    function load() {
        frappe.call({ method: 'ai_sales_agent.ai_sales_agent.workforce.workforce_dashboard.get_workforce_metrics', callback: function(r){ if(r.message) render_kpis(r.message); } });

        frappe.call({ method: 'ai_sales_agent.ai_sales_agent.workforce.workforce_dashboard.get_supervisor_leaderboard', callback: function(r){
            if(r.message && r.message.length){
                const labels = r.message.map(x => x.agent || 'Unassigned');
                const vals = r.message.map(x => x.closed_won || 0);
                try{ new frappe.Chart('#leaderboard', { data: {labels: labels, datasets: [{name: 'Closed Won', values: vals}]}, type: 'bar', height: 300 }); } catch(e){}
            }
        }});

        frappe.call({ method: 'ai_sales_agent.ai_sales_agent.workforce.workforce_dashboard.get_agent_performance', callback: function(r){
            if(r.message && r.message.length){
                const labels = r.message.map(x => x.agent || 'Unassigned');
                const vals = r.message.map(x => x.assigned_handoffs || 0);
                try{ new frappe.Chart('#agent_bar', { data: {labels: labels, datasets: [{name: 'Assigned Handoffs', values: vals}]}, type: 'bar', height: 300 }); } catch(e){}
            }
        }});
    }

    load();
    page.set_primary_action('Refresh', () => load());

}
