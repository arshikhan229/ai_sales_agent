frappe.pages['opportunity-360'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Opportunity 360',
        single_column: true
    });

    page.body.html(`
        <style>
            .opp360 {
                min-height: 900px;
                background: #f5f7fb;
                padding: 24px;
            }

            .opp360-header {
                display: flex;
                justify-content: space-between;
                gap: 16px;
                align-items: flex-start;
                margin-bottom: 20px;
            }

            .opp360-title {
                margin: 0;
                font-size: 28px;
                font-weight: 700;
                color: #0f172a;
            }

            .opp360-muted {
                color: #64748b;
                font-size: 13px;
            }

            .opp360-grid {
                display: grid;
                grid-template-columns: 2fr 1fr;
                gap: 18px;
            }

            .opp360-metrics {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 14px;
                margin-bottom: 18px;
            }

            .opp360-panel,
            .opp360-metric {
                background: #fff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(15, 23, 42, .06);
            }

            .opp360-panel {
                padding: 18px;
                margin-bottom: 18px;
            }

            .opp360-metric {
                padding: 16px;
                min-height: 110px;
            }

            .opp360-label {
                font-size: 12px;
                color: #64748b;
                text-transform: uppercase;
                letter-spacing: .04em;
                margin-bottom: 8px;
            }

            .opp360-value {
                font-size: 25px;
                font-weight: 700;
                color: #0f172a;
                line-height: 1.2;
            }

            .opp360-badge {
                display: inline-flex;
                align-items: center;
                border-radius: 999px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: 700;
            }

            .opp360-badge.green {
                background: #dcfce7;
                color: #166534;
            }

            .opp360-badge.amber {
                background: #fef3c7;
                color: #92400e;
            }

            .opp360-badge.red {
                background: #fee2e2;
                color: #991b1b;
            }

            .opp360-section-title {
                margin: 0 0 14px;
                font-size: 17px;
                font-weight: 700;
                color: #0f172a;
            }

            .opp360-row {
                padding: 12px 0;
                border-bottom: 1px solid #e5e7eb;
            }

            .opp360-row:last-child {
                border-bottom: none;
            }

            .opp360-row-title {
                font-weight: 700;
                color: #0f172a;
                margin-bottom: 4px;
            }

            .opp360-row-body {
                color: #334155;
                font-size: 13px;
                line-height: 1.45;
                white-space: pre-wrap;
            }

            .opp360-kv {
                display: grid;
                grid-template-columns: 150px 1fr;
                gap: 8px;
                padding: 8px 0;
                border-bottom: 1px solid #eef2f7;
            }

            .opp360-kv:last-child {
                border-bottom: none;
            }

            .opp360-progress {
                width: 100%;
                height: 8px;
                background: #e2e8f0;
                border-radius: 999px;
                overflow: hidden;
                margin-top: 10px;
            }

            .opp360-progress-fill {
                height: 100%;
                background: #2563eb;
            }

            @media (max-width: 1100px) {
                .opp360-grid,
                .opp360-metrics {
                    grid-template-columns: 1fr;
                }
            }
        </style>

        <div class="opp360">
            <div id="opportunity-content">
                Loading...
            </div>
        </div>
    `);

    wrapper.opportunity_360_load_current =
        load_current_opportunity;

    load_current_opportunity();

    function load_current_opportunity() {

        let route = frappe.get_route();

        if (route.length > 1) {
            load_opportunity(route[1]);
            return;
        }

        $("#opportunity-content").html(`
            <div class="opp360-panel">
                <h3 class="opp360-section-title">
                    Opportunity not selected
                </h3>
                <div class="opp360-muted">
                    Open an opportunity from the CRM pipeline.
                </div>
            </div>
        `);

    }

    function load_opportunity(opportunity) {

        frappe.call({

            method:
            "ai_sales_agent.ai_sales_agent.page.opportunity_360.opportunity_360.get_opportunity_360",

            args: {
                opportunity: opportunity
            },

            callback: function(r) {

                render_opportunity_360(
                    r.message || {}
                );

            }

        });

    }

    function render_opportunity_360(data) {

        let opp = data.opportunity || {};

        if (!opp.name) {
            $("#opportunity-content").html(`
                <div class="opp360-panel">
                    <h3 class="opp360-section-title">
                        Opportunity not found
                    </h3>
                    <div class="opp360-muted">
                        The selected opportunity could not be loaded.
                    </div>
                </div>
            `);
            return;
        }

        let probability =
            Number(opp.custom_win_probability || 0);

        let risk =
            opp.custom_risk_level ||
            data.health ||
            "Unknown";

        let risk_class =
            risk === "High" || data.health === "At Risk"
                ? "red"
                : risk === "Medium" || data.health === "Moderate"
                ? "amber"
                : "green";

        let html = `
            <div class="opp360-header">
                <div>
                    <h1 class="opp360-title">
                        ${esc(opp.name)}
                    </h1>
                    <div class="opp360-muted">
                        ${esc(opp.customer_name || opp.party_name || "")}
                        ${opp.custom_pipeline_stage ? " / " + esc(opp.custom_pipeline_stage) : ""}
                    </div>
                </div>

                <button
                    class="btn btn-primary open-customer-360"
                    data-lead="${esc_attr(opp.party_name || "")}"
                >
                    Open Customer 360
                </button>
            </div>

            <div class="opp360-metrics">
                ${metric(
                    "Deal Score",
                    opp.custom_ai_deal_score || 0,
                    "AI scoring"
                )}
                ${metric(
                    "Win Probability",
                    probability + "%",
                    "Confidence"
                )}
                ${metric(
                    "Risk Level",
                    `<span class="opp360-badge ${risk_class}">${esc(risk)}</span>`,
                    data.health || "Health"
                )}
                ${metric(
                    "Revenue Estimate",
                    money(data.revenue_estimate),
                    "Weighted value"
                )}
            </div>

            <div class="opp360-grid">
                <div>
                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            AI Summary
                        </h3>
                        <div class="opp360-row-body">
                            ${esc(opp.custom_ai_summary || "No AI summary available.")}
                        </div>
                    </div>

                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            Followups
                        </h3>
                        ${render_followups(data.followups || [])}
                    </div>

                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            Timeline
                        </h3>
                        ${render_timeline(data.timeline || [])}
                    </div>
                </div>

                <div>
                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            Revenue
                        </h3>
                        ${kv("Amount", money(opp.opportunity_amount))}
                        ${kv("Win Probability", probability + "%")}
                        ${kv("Weighted Estimate", money(data.revenue_estimate))}
                        ${kv("Expected Closing", date_value(opp.expected_closing))}
                        <div class="opp360-progress">
                            <div
                                class="opp360-progress-fill"
                                style="width:${Math.min(probability, 100)}%;"
                            ></div>
                        </div>
                    </div>

                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            Deal Details
                        </h3>
                        ${kv("Stage", opp.custom_pipeline_stage)}
                        ${kv("Status", opp.status)}
                        ${kv("Source", opp.source)}
                        ${kv("Next Action", opp.custom_next_best_action)}
                        ${kv("Lead", opp.party_name)}
                    </div>

                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            Emails
                        </h3>
                        ${render_messages(data.emails || [], "subject", "content")}
                    </div>

                    <div class="opp360-panel">
                        <h3 class="opp360-section-title">
                            WhatsApp Messages
                        </h3>
                        ${render_messages(data.whatsapp_messages || [], "direction", "message")}
                    </div>
                </div>
            </div>
        `;

        $("#opportunity-content").html(html);

    }

    function metric(label, value, subtext) {

        return `
            <div class="opp360-metric">
                <div class="opp360-label">
                    ${esc(label)}
                </div>
                <div class="opp360-value">
                    ${value}
                </div>
                <div class="opp360-muted">
                    ${esc(subtext || "")}
                </div>
            </div>
        `;

    }

    function kv(label, value) {

        return `
            <div class="opp360-kv">
                <div class="opp360-muted">
                    ${esc(label)}
                </div>
                <div>
                    ${esc(value || "")}
                </div>
            </div>
        `;

    }

    function render_followups(rows) {

        if (!rows.length) {
            return empty_state("No followups found.");
        }

        return rows.map(row => `
            <div class="opp360-row">
                <div class="opp360-row-title">
                    ${esc(row.description || row.name || "Follow-up")}
                </div>
                <div class="opp360-row-body">
                    ${esc(row.status || "")}
                    ${row.allocated_to ? " / " + esc(row.allocated_to) : ""}
                    ${row.date ? " / Due " + esc(date_value(row.date)) : ""}
                </div>
            </div>
        `).join("");

    }

    function render_timeline(rows) {

        if (!rows.length) {
            return empty_state("No timeline activity found.");
        }

        return rows.map(row => `
            <div class="opp360-row">
                <div class="opp360-row-title">
                    ${esc(row.type || "Activity")}
                    ${row.timestamp ? " / " + esc(date_value(row.timestamp)) : ""}
                </div>
                <div class="opp360-row-body">
                    <strong>${esc(row.title || "")}</strong>
                    ${row.description ? "\n" + esc(row.description) : ""}
                </div>
            </div>
        `).join("");

    }

    function render_messages(rows, title_field, body_field) {

        if (!rows.length) {
            return empty_state("No records found.");
        }

        return rows.map(row => `
            <div class="opp360-row">
                <div class="opp360-row-title">
                    ${esc(row[title_field] || row.name || "Message")}
                </div>
                <div class="opp360-muted">
                    ${esc(date_value(row.timestamp || row.creation))}
                </div>
                <div class="opp360-row-body">
                    ${esc(strip_html(row[body_field] || ""))}
                </div>
            </div>
        `).join("");

    }

    function empty_state(message) {

        return `
            <div class="opp360-muted">
                ${esc(message)}
            </div>
        `;

    }

    function money(value) {

        let number_value = Number(value || 0);

        return number_value.toLocaleString(
            undefined,
            {
                maximumFractionDigits: 0
            }
        );

    }

    function date_value(value) {

        if (!value) {
            return "";
        }

        if (frappe.datetime && frappe.datetime.str_to_user) {
            return frappe.datetime.str_to_user(value);
        }

        return value;

    }

    function strip_html(value) {

        return $("<div>")
            .html(value || "")
            .text();

    }

    function esc(value) {

        return $("<div>")
            .text(value == null ? "" : value)
            .html();

    }

    function esc_attr(value) {

        return esc(value)
            .replace(/"/g, "&quot;");

    }

};

frappe.pages['opportunity-360'].on_page_show = function(wrapper) {

    if (wrapper.opportunity_360_load_current) {
        wrapper.opportunity_360_load_current();
    }

};

$(document).on(
    "click",
    ".open-customer-360",
    function() {

        let lead =
            $(this).data("lead");

        if (!lead) {
            frappe.msgprint(
                "Lead not found"
            );
            return;
        }

        frappe.set_route(
            "customer-profile",
            lead
        );

    }
);
