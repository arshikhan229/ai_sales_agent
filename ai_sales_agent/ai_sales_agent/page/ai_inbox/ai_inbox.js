frappe.pages['ai-inbox'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'AI Unified Inbox',
		single_column: true
	});

	load_inbox(page);

	page.set_primary_action(
		"Refresh",
		() => load_inbox(page)
	);
};


function get_channel_label(channel) {

	if ((channel || "").includes("WhatsApp")) {
		return "📱 WhatsApp";
	}

	if ((channel || "").includes("Facebook")) {
		return "📘 Facebook";
	}

	if ((channel || "").includes("Email")) {
		return "📧 Email";
	}

	return channel || "";
}


function get_category_badge(category) {

	if (!category) {
		return "";
	}

	if (category.includes("Hot")) {

		return `
			<span style="
				background:#ffe5e5;
				color:#c62828;
				padding:4px 10px;
				border-radius:12px;
				font-weight:600;
			">
				🔥 Hot
			</span>
		`;
	}

	if (category.includes("Warm")) {

		return `
			<span style="
				background:#fff3cd;
				color:#856404;
				padding:4px 10px;
				border-radius:12px;
				font-weight:600;
			">
				🟡 Warm
			</span>
		`;
	}

	return `
		<span style="
			background:#f1f1f1;
			color:#555;
			padding:4px 10px;
			border-radius:12px;
			font-weight:600;
		">
			⚪ Cold
		</span>
	`;
}


function get_icp_bar(score) {

	score = score || 0;

	return `
		<div style="min-width:120px;">
			<div style="
				background:#eee;
				height:10px;
				border-radius:5px;
				overflow:hidden;
			">
				<div style="
					width:${score}%;
					height:10px;
					background:#28a745;
				"></div>
			</div>

			<div style="
				margin-top:4px;
				font-size:11px;
				font-weight:600;
			">
				${score}
			</div>
		</div>
	`;
}


function load_inbox(page) {

	frappe.call({

		method:
			'ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_inbox',

		callback: function(r) {

			let data = r.message || [];

			let hot = 0;
			let warm = 0;
			let cold = 0;
			let opportunities = 0;

			data.forEach(row => {

				let category = row.lead_category || "";

				if (category.includes("Hot")) {
					hot++;
				}
				else if (category.includes("Warm")) {
					warm++;
				}
				else {
					cold++;
				}

				if (row.opportunity) {
					opportunities++;
				}
			});

			let html = `

				<div class="row" style="margin-bottom:20px;">

					<div class="col-md-3">
						<div class="alert alert-danger">
							<h4>${hot}</h4>
							🔥 Hot Leads
						</div>
					</div>

					<div class="col-md-3">
						<div class="alert alert-warning">
							<h4>${warm}</h4>
							🟡 Warm Leads
						</div>
					</div>

					<div class="col-md-3">
						<div class="alert alert-secondary">
							<h4>${cold}</h4>
							⚪ Cold Leads
						</div>
					</div>

					<div class="col-md-3">
						<div class="alert alert-success">
							<h4>${opportunities}</h4>
							💰 Opportunities
						</div>
					</div>

				</div>

				<div style="margin-bottom:15px;">
					<input
						type="text"
						id="inbox-search"
						class="form-control"
						placeholder="Search Contact..."
					>
				</div>

				<div style="margin-bottom:15px;">

					<button class="btn btn-sm btn-default filter-btn"
						data-filter="all">
						All
					</button>

					<button class="btn btn-sm btn-primary filter-btn"
						data-filter="WhatsApp">
						📱 WhatsApp
					</button>

					<button class="btn btn-sm btn-info filter-btn"
						data-filter="Facebook">
						📘 Facebook
					</button>

					<button class="btn btn-sm btn-success filter-btn"
						data-filter="Email">
						📧 Email
					</button>

					<button class="btn btn-sm btn-danger filter-btn"
						data-filter="Hot">
						🔥 Hot
					</button>

					<button class="btn btn-sm btn-warning filter-btn"
						data-filter="Warm">
						🟡 Warm
					</button>

					<button class="btn btn-sm btn-secondary filter-btn"
						data-filter="Cold">
						⚪ Cold
					</button>

				</div>

				<table
					class="table table-bordered table-hover"
					id="inbox-table"
					style="table-layout:fixed;width:100%;"
				>

					<thead>

						<tr>

							<th>Contact</th>

							<th>Channel</th>

							<th>Messages</th>

							<th>Intent</th>

							<th>Preview</th>

							<th>Category</th>

							<th>ICP</th>

							<th>Opportunity</th>

							<th>Last Activity</th>

						</tr>

					</thead>

					<tbody>
			`;

			data.forEach(row => {

				let rowStyle = "";

				if (
					(row.lead_category || "")
					.includes("Hot")
				) {

					rowStyle =
						"background:#fff5f5;";
				}

				html += `

					<tr style="${rowStyle}">

						<td>

							<a
								href="#"
								class="open-contact"
								data-contact="${row.actual_contact}"
							>

								<b>${row.contact || ""}</b>
								<br>
								<small style="color:#888;">
									${row.channel}
								</small>

							</a>

						</td>

						<td>
							${get_channel_label(
								row.channel
							)}
						</td>

						<td>
							${row.messages || 0}
						</td>

						<td>
							${row.intent || ""}
						</td>

						<td style="
							max-width:250px;
							word-wrap:break-word;
						">
							${row.preview ? row.preview : (row.intent || "").substring(0,60)}
						</td>

						<td>
							${get_category_badge(
								row.lead_category
							)}
						</td>

						<td>
							${get_icp_bar(
								row.icp_score
							)}
						</td>

						<td>

							${
								row.opportunity
								?
								`
								<a
									href="/app/opportunity/${row.opportunity}"
									target="_blank"
									class="badge badge-success"
								>
									💰 Open
								</a>
								`
								:
								""
							}

						</td>

						<td>

							${frappe.datetime.str_to_user(
								row.last_activity || ""
							)}

						</td>

					</tr>
				`;
			});

			html += `
					</tbody>
				</table>
			`;

			$(page.body).html(html);

			// Filter button behavior
			$(page.body).find(".filter-btn").on(
				"click",
				function() {

					let filter =
						$(this).data("filter");

					// show all rows first
					$("#inbox-table tbody tr")
					.show();

					if (filter === "all") {
						return;
					}

					$("#inbox-table tbody tr")
					.each(function() {

						let text =
							$(this)
							.text()
							.toLowerCase();

						if (
							text.indexOf((filter || "").toLowerCase())
							=== -1
						) {
							$(this).hide();
						}
					});
				}
			);

			$("#inbox-search").on(
				"keyup",
				function() {

					let value =
						$(this)
						.val()
						.toLowerCase();

					$("#inbox-table tbody tr")
					.filter(function() {

						$(this).toggle(
							$(this)
							.text()
							.toLowerCase()
							.indexOf(value) > -1
						);
					});
				}
			);

			$(page.body)
			.find(".open-contact")
			.on("click", function(e) {

				e.preventDefault();

				let contact =
					$(this).data("contact");

				open_timeline(contact);
			});
		}
	});
}


function open_timeline(contact) {

	frappe.call({

		method:
		"ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_contact_timeline",

		args: {
			contact: contact
		},

		callback: function(r) {

			let rows = r.message || [];

			let html =
				`<h3>${contact}</h3><hr>`;

			rows.forEach(row => {

				html += `

					<div style="
						border:1px solid #ddd;
						padding:10px;
						margin-bottom:10px;
						border-radius:8px;
					">

						<b>${row.channel}</b>

						<br><br>

						${row.message || ""}

						<hr>

						<small>
							${row.timestamp}
						</small>

					</div>
				`;
			});

			frappe.msgprint({
				title: contact,
				message: html,
				wide: true
			});
		}
	});
}