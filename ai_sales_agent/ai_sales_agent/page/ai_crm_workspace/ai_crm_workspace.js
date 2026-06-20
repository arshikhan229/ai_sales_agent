frappe.pages['ai-crm-workspace'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI CRM Workspace',
        single_column: true
    });

    page.body.html(`

        <style>

            .crm-layout{
                display:flex;
                min-height:900px;
                background:#f5f7fb;
            }

            .crm-sidebar{
                width:260px;
                background:#0f172a;
                color:white;
                padding:20px;
            }

            .crm-logo{
                font-size:22px;
                font-weight:700;
                margin-bottom:25px;
            }

            .crm-nav{
                width:100%;
                border:none;
                background:transparent;
                color:white;
                text-align:left;
                padding:14px;
                border-radius:12px;
                margin-bottom:8px;
                cursor:pointer;
                transition:.2s;
            }

            .crm-nav:hover{
                background:#2563eb;
            }

            #workspace-content{
                flex:1;
                padding:25px;
                overflow:auto;
            }

            .crm-card{
                background:white;
                border-radius:15px;
                padding:20px;
                box-shadow:0 2px 10px rgba(0,0,0,.08);
            }

            .crm-table-row{
                cursor:pointer;
            }
            .crm-nav.active{
                background:#2563eb;
                color:white;
                font-weight:bold;
            }

            .crm-table-row:hover{
                background:#f3f4f6;
            }

        </style>

        <div class="crm-layout">

            <div class="crm-sidebar">

                <div class="crm-logo">
                    AI CRM
                </div>

                <button class="crm-nav nav-dashboard">
                    Dashboard
                </button>
                <button class="crm-nav nav-command-center">
                    Command Center
                </button>
                <button class="crm-nav nav-health">
                    Health Scores
                </button>
                <button class="crm-nav nav-recommendations">
                    AI Recommendations
                </button>

                <button class="crm-nav nav-customers">
                    Customers
                </button>

                <button class="crm-nav nav-pipeline">
                    Pipeline
                </button>

                <button class="crm-nav nav-handoffs">
                    Handoffs
                </button>
                <button class="crm-nav nav-pipeline-health">
                    Pipeline Health
                </button>

                <button class="crm-nav nav-forecast">
                    Forecast
                </button>
                <button class="crm-nav nav-risk">
                    Deal Risk Engine
                </button>

                <button class="crm-nav nav-analytics">
                    Analytics
                </button>

                <button class="crm-nav nav-copilot">
                    Copilot
                </button>

            </div>

            <div id="workspace-content">
                Loading...
            </div>

        </div>

    `);

    show_dashboard();

    $(document).on(
        "click",
        ".nav-dashboard",
        show_dashboard
    );

    $(document).on(
        "click",
        ".nav-customers",
        show_customers
    );

    $(document).on(
        "click",
        ".nav-recommendations",
        show_ai_recommendations
    );
    $(document).on(
        "click",
        ".nav-pipeline",
        show_pipeline
    );
    $(document).on(
        "click",
        ".nav-handoffs",
        show_handoffs
    );
    $(document).on(
        "click",
        ".nav-health",
        show_health_scores
    );
    $(document).on(
        "click",
        ".nav-pipeline-health",
        show_pipeline_health
    );
    $(document).on(
        "click",
        ".nav-command-center",
        show_command_center
    );
    $(document).on(
        "click",
        ".opportunity-row",
        function() {

            let opportunity =
                $(this).data("name");

            frappe.set_route(
                "opportunity-360",
                opportunity
            );

        }
    );
    $(document).on(
        "click",
        ".opportunity-card",
        function() {

            let opportunity =
                $(this).data("opportunity");

            frappe.set_route(
                "opportunity-360",
                opportunity
            );

        }
    );
    $(document).on(
        "click",
        ".handoff-row",
        function() {

            let handoff = $(this).data("name");

            frappe.set_route(
                "handoff-360",
                handoff
            );

        }
    );

    $(document).on(
        "click",
        ".nav-forecast",
        show_forecast
    );

    $(document).on(
        "click",
        ".nav-analytics",
        show_analytics
    );

    $(document).on(
        "click",
        ".nav-copilot",
        show_copilot
    );
    $(document).on(
        "click",
        ".back-customers",
        function() {

            $(".nav-customers").trigger("click");

        }
    );
    $(document).on(
        "click",
        ".nav-risk",
        show_deal_risk
    );
    $(document).on(
        "click",
        ".customer-row",
        function() {

            let name = $(this).data("name");

            show_customer_360(name);

        }
    );
    $(document).on(
        "click",
        ".crm-nav",
        function() {

            $(".crm-nav").removeClass("active");

            $(this).addClass("active");

        }
    );

    function show_dashboard() {
    $(".nav-dashboard").addClass("active");   

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_dashboard_v2",

        callback: function(r) {

            let d = r.message || {};

            let leads_html = "";
            let opp_html = "";
            let activity_html = "";

            (d.recent_leads || []).forEach(row => {

                leads_html += `
                    <tr
                        class="customer-row crm-table-row"
                        data-name="${row.name}"
                    >
                        <td>${row.lead_name || ""}</td>
                        <td>${row.source || ""}</td>
                        <td>${row.icp_score || 0}</td>
                    </tr>
                `;

            });

            (d.recent_opportunities || []).forEach(row => {

                opp_html += `
                    <tr
                        class="opportunity-row crm-table-row"
                        data-name="${row.name}"
                    >
                        <td>${row.name}</td>
                        <td>${row.custom_pipeline_stage || ""}</td>
                        <td>${row.opportunity_amount || 0}</td>
                    </tr>
                `;

            });

            (d.recent_activities || []).forEach(row => {

                activity_html += `
                    <div style="
                        padding:10px;
                        border-bottom:1px solid #eee;
                    ">
                        <strong>${row.type}</strong><br>
                        ${row.title}
                    </div>
                `;

            });

            $("#workspace-content").html(`

                <h2 style="margin-bottom:20px;">
                    Dashboard
                </h2>

                <div style="
                    display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:20px;
                    margin-bottom:20px;
                ">

                    <div class="crm-card">
                        <h5>🔥 Hot Leads</h5>
                        <h2>${d.hot_leads || 0}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>👥 Open Handoffs</h5>
                        <h2>${d.open_handoffs || 0}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>💰 Pipeline</h5>
                        <h2>${d.pipeline_value || 0}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>📈 Forecast</h5>
                        <h2>${d.forecast_value || 0}</h2>
                    </div>

                </div>

                <div style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:20px;
                    margin-bottom:20px;
                ">

                    <div class="crm-card">

                        <h4>Recent Leads</h4>

                        <table class="table">

                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>Source</th>
                                    <th>Score</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${leads_html}
                            </tbody>

                        </table>

                    </div>

                    <div class="crm-card">

                        <h4>Recent Opportunities</h4>

                        <table class="table">

                            <thead>
                                <tr>
                                    <th>Opportunity</th>
                                    <th>Stage</th>
                                    <th>Amount</th>
                                </tr>
                            </thead>

                            <tbody>
                                ${opp_html}
                            </tbody>

                        </table>

                    </div>

                </div>

                <div class="crm-card">

                    <h4>Recent Activity</h4>

                    ${activity_html}

                </div>

            `);

        }

    });

}

    function show_customers() {

        frappe.call({

            method:
            "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_customers",

            callback: function(r) {

                let rows = r.message || [];

                let html = `

                    <h2 style="margin-bottom:20px;">
                        Customers
                    </h2>

                    <div class="crm-card">

                        <table class="table">

                            <thead>

                                <tr>

                                    <th>Name</th>

                                    <th>Source</th>

                                    <th>Category</th>

                                    <th>Opportunity</th>

                                </tr>

                            </thead>

                            <tbody>

                `;

                rows.forEach(row => {

                    html += `

                        <tr
                            class="customer-row crm-table-row"
                            data-name="${row.name}"
                        >

                            <td>
                                ${row.lead_name || ""}
                            </td>

                            <td>
                                ${row.source || ""}
                            </td>

                            <td>
                                ${row.lead_category || ""}
                            </td>

                            <td>
                                ${row.custom_erp_opportunity || ""}
                            </td>

                        </tr>

                    `;

                });

                html += `

                            </tbody>

                        </table>

                    </div>

                `;

                $("#workspace-content").html(html);

            }

        });

    }
    

    function show_pipeline() {

        frappe.call({

            method:
            "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_pipeline_board",

            callback: function(r) {

                let rows = r.message || [];

                let stages = {
                    "Qualified": [],
                    "Discovery": [],
                    "Proposal": [],
                    "Negotiation": [],
                    "Closed Won": []
                };

                rows.forEach(row => {

                    let stage =
                        row.custom_pipeline_stage ||
                        "Qualified";

                    if (!stages[stage]) {
                        stages[stage] = [];
                    }

                    stages[stage].push(row);

                });

                let html = `

                    <h2 style="margin-bottom:20px;">
                        Sales Pipeline
                    </h2>

                    <div style="
                        display:grid;
                        grid-template-columns:repeat(5,1fr);
                        gap:15px;
                    ">
                `;

                Object.keys(stages).forEach(stage => {

                    html += `

                        <div class="crm-card">

                            <h4>
                                ${stage}
                            </h4>

                            <hr>
                    `;

                    stages[stage].forEach(opp => {

                        html += `

                            <div
                                class="crm-card opportunity-card"
                                data-opportunity="${opp.name}"
                                style="
                                    margin-bottom:10px;
                                    background:#f8fafc;
                                    cursor:pointer;
                                "
                            >

                                <strong>
                                    ${opp.name}
                                </strong>

                                <br>

                                Amount:
                                <div style="
                                    margin-top:8px;
                                    color:${
                                        (opp.custom_win_probability || 0) >= 70
                                            ? '#16a34a'
                                            : (opp.custom_win_probability || 0) >= 40
                                            ? '#ca8a04'
                                            : '#dc2626'
                                    };
                                    font-weight:bold;
                                ">
                                    Win:
                                    ${opp.custom_win_probability || 0}%
                                </div>
                                `;
                            });
                            html += `</div>`;
                        });
                        html += `</div>`;
                        $("#workspace-content").html(html);
                    }
                });
            }
        };


function show_handoffs() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_handoffs",

        callback: function(r) {

            let rows = r.message || [];

            let html = `

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:20px;
                ">

                    <h2>
                        Open Handoffs
                    </h2>

                    <span class="badge badge-primary">
                        Total: ${rows.length}
                    </span>

                </div>

                <div class="crm-card">

                    <table class="table">

                        <thead>

                            <tr>

                                <th>Assigned To</th>

                                <th>Status</th>

                                <th>Opportunity</th>

                                <th>Action</th>

                            </tr>

                        </thead>

                        <tbody>

            `;

            if (!rows.length) {

                html += `

                    <tr>

                        <td colspan="4" style="text-align:center;">

                            No Open Handoffs Found

                        </td>

                    </tr>

                `;

            }

            rows.forEach(row => {

                html += `

                    <tr
                        class="handoff-row crm-table-row"
                        data-name="${row.name}"
                    >

                        <td>
                            ${row.assigned_to || ""}
                        </td>

                        <td>

                            <span
                                style="
                                    padding:4px 10px;
                                    border-radius:20px;
                                    background:#dbeafe;
                                    color:#1e40af;
                                    font-size:12px;
                                "
                            >

                                ${row.status || ""}

                            </span>

                        </td>

                        <td>

                            ${row.opportunity || ""}

                        </td>

                        <td>

                            <button
                                class="btn btn-sm btn-primary handoff-open-btn"
                                data-name="${row.name}"
                            >
                                Open
                            </button>

                        </td>

                    </tr>

                `;

            });

            html += `

                        </tbody>

                    </table>

                </div>

            `;

            $("#workspace-content").html(html);

        },

        error: function() {

            $("#workspace-content").html(`

                <div class="crm-card">

                    <h3>
                        Failed To Load Handoffs
                    </h3>

                    <p>
                        Please refresh and try again.
                    </p>

                </div>

            `);

        }

    });

}
function show_customer_360(ai_lead) {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.customer_360.customer_360.get_customer_360",

        args: {
            ai_lead: ai_lead
        },

        callback: function(r) {

            let data = r.message || {};

            let lead = data.lead || {};
            let opp = data.opportunity || {};

            let conversations_html = "";

            (data.conversations || []).forEach(row => {

                conversations_html += `

                    <div class="crm-card" style="margin-bottom:10px;">

                        <strong>
                            ${row.channel || ""}
                        </strong>

                        <br>

                        ${row.message || ""}

                        <hr>

                        <small>
                            ${row.timestamp || ""}
                        </small>

                    </div>

                `;

            });

            let handoffs_html = "";

            (data.handoffs || []).forEach(row => {

                handoffs_html += `

                    <tr>

                        <td>
                            ${row.assigned_to || ""}
                        </td>

                        <td>
                            ${row.status || ""}
                        </td>

                        <td>
                            ${row.creation || ""}
                        </td>

                    </tr>

                `;

            });

            $("#workspace-content").html(`

                <button
                    class="btn btn-primary back-customers"
                    style="margin-bottom:20px;"
                >
                    ← Back to Customers
                </button>

                <div class="crm-card">

                    <h2>
                        ${lead.lead_name || ""}
                    </h2>

                    <hr>

                    <p>
                        <b>Source:</b>
                        ${lead.source || ""}
                    </p>

                    <p>
                        <b>Category:</b>
                        ${lead.lead_category || ""}
                    </p>

                    <p>
                        <b>Intent:</b>
                        ${lead.intent_type || ""}
                    </p>

                    <p>
                        <b>ICP Score:</b>
                        ${lead.icp_score || 0}
                    </p>

                    <p>
                        <b>ERP Lead:</b>
                        ${lead.custom_erp_lead || ""}
                    </p>

                    <p>
                        <b>Opportunity:</b>
                        ${lead.custom_erp_opportunity || ""}
                    </p>

                </div>

                <br>

                <div class="crm-card">

                    <h3>
                        AI Intelligence
                    </h3>

                    <hr>

                    <p>
                        <b>Deal Score:</b>
                        ${opp.custom_ai_deal_score || 0}
                    </p>

                    <p>
                        <b>Win Probability:</b>
                        ${opp.custom_win_probability || 0}%
                    </p>

                    <p>
                        <b>Risk Level:</b>
                        ${opp.custom_risk_level || ""}
                    </p>

                    <p>
                        <b>Next Best Action:</b>
                        ${opp.custom_next_best_action || ""}
                    </p>

                    <p>
                        <b>AI Summary:</b>
                        ${opp.custom_ai_summary || ""}
                    </p>

                </div>

                <br>

                <div class="crm-card">

                    <h3>
                        Conversations
                    </h3>

                    ${conversations_html || "No conversations found"}

                </div>

                <br>

                <div class="crm-card">

                    <h3>
                        Handoffs
                    </h3>

                    <table class="table">

                        <thead>

                            <tr>

                                <th>Assigned To</th>

                                <th>Status</th>

                                <th>Date</th>

                            </tr>

                        </thead>

                        <tbody>

                            ${handoffs_html}

                        </tbody>

                    </table>

                </div>

            `);

        }

    });

}

function show_copilot() {

    $("#workspace-content").html(`

        <div class="crm-card">

            <h2>
                AI Sales Copilot
            </h2>

            <div style="margin-top:20px;">

                <input
                    type="text"
                    id="copilot-question"
                    class="form-control"
                    placeholder="Ask something..."
                >

            </div>

            <div style="margin-top:15px;">

                <button
                    class="btn btn-primary run-copilot"
                >
                    Ask Copilot
                </button>

            </div>

            <hr>

            <div
                id="copilot-result"
                style="margin-top:20px;"
            >
            </div>

        </div>

    `);

}

$(document).on(
    "click",
    ".run-copilot",
    function() {

        let question =
            $("#copilot-question").val();

        frappe.call({

            method:
            "ai_sales_agent.ai_sales_agent.utils.sales_copilot_api.ask",

            args: {
                question: question
            },

            callback: function(r) {

                render_copilot_result(
                    r.message
                );

            }

        });

    }
);

function render_copilot_result(result) {

    if (!result) {

        $("#copilot-result").html(
            "No response."
        );

        return;
    }

    if (result.type === "table") {

        let html = `

            <h4>
                ${result.title || ""}
            </h4>

            <table class="table table-bordered">

                <thead>
                    <tr>
        `;

        let first =
            result.rows?.[0] || {};

        Object.keys(first).forEach(col => {

            html += `<th>${col}</th>`;

        });

        html += `
                    </tr>
                </thead>

                <tbody>
        `;

        result.rows.forEach(row => {

            html += "<tr>";

            Object.values(row).forEach(v => {

                html += `<td>${v}</td>`;

            });

            html += "</tr>";

        });

        html += `
                </tbody>
            </table>
        `;

        $("#copilot-result").html(html);

        return;
    }

    $("#copilot-result").html(
        JSON.stringify(
            result,
            null,
            2
        )
    );

}

function show_command_center() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_command_center",

        callback: function(r) {

            let d = r.message || {};

            let opp_html = "";

            (d.top_opportunities || []).forEach(row => {

                opp_html += `

                    <tr>

                        <td>${row.name}</td>

                        <td>${row.opportunity_amount}</td>

                        <td>${row.custom_win_probability}%</td>

                    </tr>

                `;

            });

            $("#workspace-content").html(`

                <h2>⭐ AI Command Center</h2>

                <div style="
                    display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:20px;
                    margin-bottom:20px;
                ">

                    <div class="crm-card">
                        <h5>🔥 Hot Leads</h5>
                        <h2>${d.hot_leads}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>⚠️ Risk Deals</h5>
                        <h2>${d.risk_deals}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>📋 Followups</h5>
                        <h2>${d.followups}</h2>
                    </div>

                    <div class="crm-card">
                        <h5>👥 Handoffs</h5>
                        <h2>${d.handoffs}</h2>
                    </div>

                </div>

                <div class="crm-card">

                    <h4>
                        Top Opportunities
                    </h4>

                    <table class="table">

                        <thead>

                            <tr>

                                <th>Opportunity</th>

                                <th>Amount</th>

                                <th>Win %</th>

                            </tr>

                        </thead>

                        <tbody>

                            ${opp_html}

                        </tbody>

                    </table>

                </div>

                <br>

                <div class="crm-card">

                    <h4>
                        🤖 AI Recommendation
                    </h4>

                    <ul>

                        <li>
                            Follow up high value deals today.
                        </li>

                        <li>
                            Focus on opportunities above 70% win probability.
                        </li>

                        <li>
                            Resolve open handoffs immediately.
                        </li>

                    </ul>

                </div>

            `);

        }

    });

}

function show_forecast() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_forecast",

        callback: function(r) {

            let d = r.message || {};

            $("#workspace-content").html(`

                <h2>Revenue Forecast</h2>

                <div class="crm-card">

                    <p>
                        Pipeline Value:
                        <strong>${d.pipeline_value || 0}</strong>
                    </p>

                    <p>
                        Forecast Value:
                        <strong>${d.forecast_value || 0}</strong>
                    </p>

                    <p>
                        Won Revenue:
                        <strong>${d.won_value || 0}</strong>
                    </p>

                </div>

            `);

        }

    });

}

function show_health_scores() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_customer_health_scores",

        callback: function(r) {

            let rows = r.message || [];

            let html = `
                <h2>
                    Customer Health Scores
                </h2>

                <div class="crm-card">

                    <table class="table">

                        <thead>

                            <tr>

                                <th>Customer</th>

                                <th>Score</th>

                                <th>Status</th>

                            </tr>

                        </thead>

                        <tbody>
            `;

            rows.forEach(row => {

                let color =
                    row.status === "Healthy"
                    ? "#16a34a"
                    : row.status === "Watch"
                    ? "#ca8a04"
                    : "#dc2626";

                html += `

                    <tr>

                        <td>
                            ${row.lead_name}
                        </td>

                        <td>
                            ${row.score}
                        </td>

                        <td>

                            <span
                                style="
                                    color:${color};
                                    font-weight:bold;
                                "
                            >

                                ${row.status}

                            </span>

                        </td>

                    </tr>

                `;

            });

            html += `
                    </tbody>
                </table>
            </div>
            `;

            $("#workspace-content").html(html);

        }

    });

}

function show_pipeline_health() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_pipeline_health",

        callback: function(r) {

            let d = r.message || {};

            $("#workspace-content").html(`

                <h2>Pipeline Health</h2>

                <div style="
                    display:grid;
                    grid-template-columns:repeat(4,1fr);
                    gap:20px;
                ">

                    <div class="crm-card">
                        <h4>🔥 Likely Close</h4>
                        <h2>${d.likely_close}</h2>
                    </div>

                    <div class="crm-card">
                        <h4>⚠️ Stuck Deals</h4>
                        <h2>${d.stuck}</h2>
                    </div>

                    <div class="crm-card">
                        <h4>🔴 High Risk</h4>
                        <h2>${d.high_risk}</h2>
                    </div>

                    <div class="crm-card">
                        <h4>💰 Big Deals</h4>
                        <h2>${d.big_deals}</h2>
                    </div>

                </div>

            `);

        }

    });

}

function show_analytics() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_analytics",

        callback: function(r) {

            let d = r.message || {};

            $("#workspace-content").html(`

                <h2>Analytics</h2>

                <div style="
                    display:grid;
                    grid-template-columns:repeat(2,1fr);
                    gap:20px;
                ">

                    <div class="crm-card">

                        <h4>Lead Sources</h4>

                        <p>WhatsApp: ${d.whatsapp}</p>

                        <p>Facebook: ${d.facebook}</p>

                        <p>Email: ${d.email}</p>

                    </div>

                    <div class="crm-card">

                        <h4>Lead Categories</h4>

                        <p>Hot: ${d.hot}</p>

                        <p>Warm: ${d.warm}</p>

                        <p>Cold: ${d.cold}</p>

                    </div>

                </div>

            `);

        }

    });

}

function show_deal_risk() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_deal_risk_engine",

        callback: function(r) {

            let rows =
                r.message || [];

            let html = `

                <h2>
                    Deal Risk Engine
                </h2>

                <div class="crm-card">

                    <table class="table">

                        <thead>

                            <tr>

                                <th>Opportunity</th>

                                <th>Amount</th>

                                <th>Risk Score</th>

                                <th>Status</th>

                            </tr>

                        </thead>

                        <tbody>
            `;

            rows.forEach(row => {

                let color =
                    row.status === "Critical"
                    ? "#dc2626"
                    : row.status === "At Risk"
                    ? "#ca8a04"
                    : "#16a34a";

                html += `

                    <tr>

                        <td>${row.name}</td>

                        <td>${row.amount || 0}</td>

                        <td>${row.risk_score}</td>

                        <td
                            style="
                                color:${color};
                                font-weight:bold;
                            "
                        >
                            ${row.status}
                        </td>

                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
                </div>
            `;

            $("#workspace-content").html(html);

        }

    });

}

function show_ai_recommendations() {

    frappe.call({

        method:
        "ai_sales_agent.ai_sales_agent.page.ai_crm_workspace.ai_crm_workspace.get_ai_recommendations",

        callback: function(r) {

            let rows =
                r.message || [];

            let html = `

                <h2>
                    AI Recommendations
                </h2>
            `;

            rows.forEach(row => {

                let color =
                    row.priority === "High"
                    ? "#dc2626"
                    : "#ca8a04";

                html += `

                    <div
                        class="crm-card"
                        style="
                            margin-bottom:10px;
                            border-left:5px solid ${color};
                        "
                    >

                        <strong>
                            ${row.priority}
                        </strong>

                        <br>

                        ${row.message}

                    </div>

                `;

            });

            $("#workspace-content").html(
                html
            );

        }

    });

}