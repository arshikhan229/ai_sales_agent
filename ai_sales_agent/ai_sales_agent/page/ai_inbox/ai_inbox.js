frappe.pages['ai-inbox'].on_page_load = function(wrapper) {

	let page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'AI Unified Inbox',
		single_column: true
	});

	load_inbox(page);
};


function load_inbox(page) {

	frappe.call({
		method:
			'ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_inbox',

		callback: function(r) {

			let data = r.message || [];

			let html = `
				<table class="table table-bordered"
					   style="table-layout:fixed;width:100%;">
					<thead>
						<tr>
							<th>Contact</th>
							<th>Messages</th>
							<th>Intent</th>
							<th>Category</th>
							<th>ICP</th>
							<th>Opportunity</th>
							<th>Last Activity</th>
						</tr>
					</thead>
					<tbody>
			`;

			data.forEach(row => {

				html += `
					<tr>
						<td>
							<a href="#"
							   class="open-contact"
							   data-contact="${row.actual_contact}">
								${row.contact || ""}
							</a>
						</td>

						<td>${row.messages || 0}</td>

						<td>${row.intent || ""}</td>

						<td>${row.lead_category || ""}</td>

						<td>${row.icp_score || 0}</td>

						<td>
							${
								row.opportunity
								?
								`<a href="/app/opportunity/${row.opportunity}">
									${row.opportunity}
								</a>`
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

			let html = `<h3>${contact}</h3><hr>`;

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

						<small>${row.timestamp}</small>
					</div>
				`;
			});

			frappe.msgprint({
				title: contact,
				message: html
			});
		}
	});
}