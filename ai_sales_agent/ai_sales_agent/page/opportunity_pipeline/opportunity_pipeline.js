frappe.pages['opportunity-pipeline'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Opportunity Pipeline',
        single_column: true
    });

    page.set_primary_action(
        "Refresh",
        () => load_pipeline()
    );

    page.body.html(`
        <div id="pipeline-summary"></div>

        <div
            id="pipeline-board"
            style="
                display:flex;
                gap:20px;
                overflow-x:auto;
            "
        ></div>
    `);

    load_pipeline();

    function load_pipeline() {

        frappe.call({
            method:
            "ai_sales_agent.ai_sales_agent.page.opportunity_pipeline.opportunity_pipeline.get_pipeline_data",

            callback: function(r) {

                render_board(
                    r.message || {}
                );

            }
        });
    }

    function render_board(data) {

        const stages =
            data.stages || {};

        const stage_totals =
            data.stage_totals || {};

        $("#pipeline-summary").html(`

            <div
                class="card"
                style="
                    padding:15px;
                    margin-bottom:20px;
                "
            >

                <h4>
                    Pipeline Summary
                </h4>

                <p>
                    <b>Total Pipeline:</b>
                    ${format_currency(
                        data.total_pipeline_value || 0
                    )}
                </p>

                <p>
                    <b>Total Forecast:</b>
                    ${format_currency(
                        data.total_forecast_value || 0
                    )}
                </p>

            </div>

        `);

        let html = "";

        Object.keys(stages).forEach(stage => {

            let cards = "";

            (stages[stage] || []).forEach(opp => {

                cards += `

                    <div
                        class="pipeline-card card"
                        draggable="true"
                        data-opportunity="${opp.name}"
                        style="
                            padding:10px;
                            margin-bottom:10px;
                            cursor:move;
                        "
                    >

                        <b>${opp.name}</b>

                        <br>

                        ${opp.party_name || ""}

                        <br>

                        <small>

                            Value:
                            ${format_currency(
                                opp.opportunity_amount || 0
                            )}

                        </small>

                        <br>

                        <small>

                            Probability:
                            ${opp.probability || 0}%

                        </small>

                        <br>

                        <small>

                            Forecast:
                            ${format_currency(
                                opp.forecast_amount || 0
                            )}

                        </small>

                    </div>

                `;
            });

            html += `

                <div
                    class="pipeline-column"
                    data-stage="${stage}"
                    style="
                        min-width:300px;
                        background:#f7f7f7;
                        padding:10px;
                        border-radius:8px;
                    "
                >

                    <h4>
                        ${stage}
                        (${(stages[stage] || []).length})
                    </h4>

                    <div
                        style="
                            font-size:12px;
                            margin-bottom:10px;
                            color:#666;
                        "
                    >

                        Revenue:
                        ${format_currency(
                            stage_totals[stage] || 0
                        )}

                    </div>

                    <div class="drop-zone">

                        ${cards}

                    </div>

                </div>

            `;
        });

        $("#pipeline-board").html(
            html
        );

        bind_drag_events();
    }

    function bind_drag_events() {

        let dragged = null;

        document
            .querySelectorAll(".pipeline-card")
            .forEach(card => {

                card.addEventListener(
                    "dragstart",
                    function() {

                        dragged = this;

                    }
                );

            });

        document
            .querySelectorAll(".pipeline-column")
            .forEach(column => {

                column.addEventListener(
                    "dragover",
                    function(e) {

                        e.preventDefault();

                    }
                );

                column.addEventListener(
                    "drop",
                    function(e) {

                        e.preventDefault();

                        if (!dragged) {
                            return;
                        }

                        const stage =
                            this.dataset.stage;

                        const opportunity =
                            dragged.dataset.opportunity;

                        frappe.call({

                            method:
                            "ai_sales_agent.ai_sales_agent.page.opportunity_pipeline.opportunity_pipeline.update_pipeline_stage",

                            args: {
                                opportunity:
                                    opportunity,
                                stage:
                                    stage
                            },

                            callback: function() {

                                load_pipeline();

                            }

                        });

                    }
                );

            });
    }

    function format_currency(value) {

        return new Intl.NumberFormat(
            "en-US",
            {
                style: "currency",
                currency: "USD"
            }
        ).format(value || 0);

    }
};