frappe.pages['sales-copilot'].on_page_load = function(wrapper) {

    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'AI Sales Copilot',
        single_column: true
    });

    page.body.html(`

        <div style="max-width:1000px;">

            <div class="card p-3 mb-3">

                <input
                    type="text"
                    id="copilot-question"
                    class="form-control"
                    placeholder="Ask AI Sales Copilot..."
                >

                <br>

                <button
                    class="btn btn-primary"
                    id="ask-copilot"
                >
                    Ask
                </button>

            </div>

            <div id="copilot-result"></div>

        </div>

    `);

    $(document)
        .off("click", "#ask-copilot")
        .on("click", "#ask-copilot", function() {

            let question =
                $("#copilot-question").val();

            if (!question) {
                frappe.msgprint("Enter a question");
                return;
            }

            frappe.call({

                method:
                "ai_sales_agent.ai_sales_agent.utils.sales_copilot_api.ask",

                args: {
                    question: question
                },

                callback: function(r) {

                    render_result(
                        r.message
                    );

                }
            });

        });

    function render_result(data) {

        if (!data) {
            return;
        }

        // ==========================
        // ACTION RESULTS
        // ==========================

        if (data.type === "action") {

            $("#copilot-result").html(`

                <div class="alert alert-success">

                    <h4>Action Executed</h4>

                    <pre>
${JSON.stringify(
    data.result,
    null,
    2
)}
                    </pre>

                </div>

            `);

            return;
        }

        // ==========================
        // SIMPLE MESSAGE
        // ==========================

        if (data.type === "message") {

            $("#copilot-result").html(
                `
                <div class="alert alert-info">
                    ${data.message}
                </div>
                `
            );

            return;
        }

        // ==========================
        // FORECAST
        // ==========================

        if (data.type === "forecast") {

            let d = data.data;

            $("#copilot-result").html(`

                <div class="card p-3">

                    <h4>Revenue Forecast</h4>

                    <table class="table table-bordered">

                        <tr>
                            <td>Pipeline Revenue</td>
                            <td>${d.pipeline_value}</td>
                        </tr>

                        <tr>
                            <td>Forecast Revenue</td>
                            <td>${d.forecast_value}</td>
                        </tr>

                        <tr>
                            <td>Won Revenue</td>
                            <td>${d.won_value}</td>
                        </tr>

                    </table>

                </div>

            `);

            return;
        }

        // ==========================
        // TABLE RESULTS
        // ==========================

        let html = `

            <div class="card p-3">

                <h4>${data.title || "Results"}</h4>

                <table class="table table-bordered">

                    <tbody>

        `;

        (data.rows || []).forEach(row => {

            html += `

                <tr>

                    <td>

                        <pre style="margin:0;">
${JSON.stringify(
    row,
    null,
    2
)}
                        </pre>

                    </td>

                </tr>

            `;
        });

        html += `

                    </tbody>

                </table>

            </div>

        `;

        $("#copilot-result").html(
            html
        );
    }

};