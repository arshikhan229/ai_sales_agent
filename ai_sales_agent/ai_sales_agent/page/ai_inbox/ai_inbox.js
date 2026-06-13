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
		if (!category) return "";
		if (category.includes("Hot")) {
			return '<span style="background:#ffe5e5;color:#a00;padding:6px 12px;border-radius:12px;font-weight:700;">🔥 Hot</span>';
		}
		if (category.includes("Warm")) {
			return '<span style="background:#fff7e6;color:#a60;padding:6px 12px;border-radius:12px;font-weight:700;">🟡 Warm</span>';
		}
		return '<span style="background:#f1f1f1;color:#555;padding:6px 12px;border-radius:12px;font-weight:600;">⚪ Cold</span>';
	}


	function get_icp_bar(score) {
		score = score || 0;
		return '<div style="min-width:120px;">'
			+ '<div style="background:#eee;height:10px;border-radius:5px;overflow:hidden;">'
			+ '<div style="width:' + score + '%;height:10px;background:#28a745;"></div>'
			+ '</div>'
			+ '<div style="margin-top:4px;font-size:11px;font-weight:600;">' + score + '</div>'
			+ '</div>';
	}


	function load_inbox(page) {
		frappe.call({
			method: 'ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_inbox',
			callback: function(r) {
				let resp = r.message || {};
				let data = resp.rows || [];

				let hot = 0, warm = 0, cold = 0, opportunities = 0;
				let open_handoffs = resp.open_handoffs || 0;
				let total_handoffs = resp.total_handoffs || 0;

				let assigned_handoffs = 0;

				data.forEach(row => {
					let category = row.lead_category || "";
					if (category.includes("Hot")) hot++;
					else if (category.includes("Warm")) warm++;
					else cold++;
					if (row.opportunity) opportunities++;
					if (row.handoff_assigned_to) assigned_handoffs++;
				});

				let html = '';

				html += '<div class="row" style="margin-bottom:20px;">';
				html += '<div class="col-md-2"><div class="alert alert-danger"><h4>' + hot + '</h4>🔥 Hot Leads</div></div>';
				html += '<div class="col-md-2"><div class="alert alert-warning"><h4>' + warm + '</h4>🟡 Warm Leads</div></div>';
				html += '<div class="col-md-2"><div class="alert alert-secondary"><h4>' + cold + '</h4>⚪ Cold Leads</div></div>';
				html += '<div class="col-md-2"><div class="alert alert-success"><h4>' + opportunities + '</h4>💰 Opportunities</div></div>';
				html += '<div class="col-md-2"><div class="alert alert-info"><h4>' + open_handoffs + '</h4>👤 Open Handoffs</div></div>';
				html += '<div class="col-md-2"><div class="alert alert-primary"><h4>' + assigned_handoffs + '</h4>✅ Assigned Handoffs</div></div>';
				html += '</div>';

				html += '<div style="margin-bottom:15px;">'
					+ '<input type="text" id="inbox-search" class="form-control" placeholder="Search Contact...">'
					+ '</div>';

					html += '<div style="margin-bottom:15px;">'
					+ '<button class="btn btn-sm btn-default filter-btn" data-filter="all">All</button> '
					+ '<button class="btn btn-sm btn-danger filter-btn" data-filter="Open Handoffs">👤 Open Handoffs</button> '
					+ '<button class="btn btn-sm btn-primary filter-btn" data-filter="Assigned To Me">👤 Assigned To Me</button> '
					+ '<button class="btn btn-sm btn-primary filter-btn" data-filter="My Leads">📌 My Leads</button> '
					+ '<button class="btn btn-sm btn-primary filter-btn" data-filter="WhatsApp">📱 WhatsApp</button> '
					+ '<button class="btn btn-sm btn-info filter-btn" data-filter="Facebook">📘 Facebook</button> '
					+ '<button class="btn btn-sm btn-success filter-btn" data-filter="Email">📧 Email</button> '
					+ '<button class="btn btn-sm btn-danger filter-btn" data-filter="Hot">🔥 Hot</button> '
					+ '<button class="btn btn-sm btn-warning filter-btn" data-filter="Warm">🟡 Warm</button> '
					+ '<button class="btn btn-sm btn-secondary filter-btn" data-filter="Cold">⚪ Cold</button>'
					+ '</div>';

				html += '<div style="overflow-x:auto;width:100%;">';
				html += '<table class="table table-bordered table-hover" id="inbox-table" style="width:100%;min-width:1800px;table-layout:auto;">';
				html += '<thead><tr>'
					+ '<th style="min-width:220px;">Contact</th>'
					+ '<th style="min-width:100px;">Channel</th>'
					+ '<th style="min-width:80px;text-align:center;">Messages</th>'
					+ '<th style="min-width:150px;">Intent</th>'
					+ '<th style="min-width:350px;">Preview</th>'
					+ '<th style="min-width:120px;">Category</th>'
					+ '<th style="min-width:120px;">ICP</th>'
					+ '<th style="min-width:140px;">Opportunity</th>'
					+ '<th style="min-width:140px;">SLA</th>'
					+ '<th style="min-width:100px;">Follow-ups</th>'
					+ '<th style="min-width:160px;">Last Follow-up</th>'
					+ '<th style="min-width:160px;">Next Due</th>'
					+ '<th style="min-width:260px;">AI Reply</th>'
					+ '<th style="min-width:140px;">Next Action</th>'
					+ '<th style="min-width:120px;">Copilot</th>'
					+ '<th style="min-width:260px;">Handoff</th>'
					+ '<th style="min-width:180px;">Assigned</th>'
					+ '<th style="min-width:80px;text-align:center;">Tasks</th>'
					+ '<th style="min-width:180px;">Last Activity</th>'
					+ '</tr></thead>';

				html += '<tbody>';

				data.forEach(row => {
					let rowStyle = '';
					if ((row.lead_category || '').includes('Hot')) rowStyle = 'background:#fff5f5;';
					if (row.handoff_name) rowStyle += 'border-left:4px solid #ffb74d;';

					// assigned_handoffs counted earlier

					let opportunity_html = '';
					if (row.opportunity) {
						opportunity_html = '<a href="/app/opportunity/' + row.opportunity + '" target="_blank" class="badge badge-success">💰 Open</a>';
					}


						// Build Handoff column badges
						let handoff_html = '';
						if (row.handoff_name) {
							handoff_html += '<span style="background:#e3f2fd;color:#1565c0;padding:4px 8px;border-radius:8px;font-weight:600;margin-right:6px;">👤 Human Handoff</span>';
							// status badge
							if ((row.handoff_status || '').toLowerCase() === 'open') {
								handoff_html += '<span style="background:#fff5e6;color:#a00;padding:4px 8px;border-radius:8px;font-weight:600;margin-right:6px;">🔥 Open Handoff</span>';
							}
							// assigned badge
							if (row.handoff_assigned_to) {
								handoff_html += '<span style="background:#e8f5e9;color:#2e7d32;padding:4px 8px;border-radius:8px;font-weight:600;">✅ Assigned: ' + (row.handoff_assigned_to) + '</span>';
							}
							// link to handoff
							handoff_html = '<a href="/app/ai-handoff/' + row.handoff_name + '" target="_blank" style="text-decoration:none;">' + handoff_html + '</a>';

							// Claim button: show only when handoff exists and status is Open
							try {
								if ((row.handoff_status || '').toLowerCase() === 'open') {
									handoff_html += ' <button class="btn btn-sm btn-outline-primary claim-handoff" data-handoff="' + row.handoff_name + '">📌 Claim Lead</button>';
								}
							} catch (e) {
								// ignore
							}

							// Workspace button
							try {
								handoff_html += ' <button class="btn btn-primary btn-sm open-workspace" data-handoff="' + row.handoff_name + '">Workspace</button>';
							} catch (e) {
								// ignore
							}
						}

					html += '<tr style="' + rowStyle + '" data-handoff-name="' + (row.handoff_name || '') + '" data-handoff-status="' + (row.handoff_status || '') + '" data-handoff-assigned="' + (row.handoff_assigned_to || '') + '">';
					html += '<td style="min-width:220px;"><a href="#" class="open-contact" data-contact="' + (row.actual_contact || '') + '"><b>' + (row.contact || '') + '</b><br><small style="color:#888;">' + (row.channel || '') + '</small></a></td>';
					html += '<td style="min-width:100px;">' + get_channel_label(row.channel) + '</td>';
					html += '<td style="min-width:80px;text-align:center;">' + (row.messages || 0) + '</td>';
					html += '<td style="min-width:150px;">' + (row.intent || '') + '</td>';
					html += '<td style="min-width:350px;max-width:450px;word-break:break-word;">' + (row.preview ? row.preview : ((row.intent || '').substring(0,60))) + '</td>';
					html += '<td style="min-width:120px;">' + get_category_badge(row.lead_category) + '</td>';
					html += '<td style="min-width:120px;">' + get_icp_bar(row.icp_score) + '</td>';
					html += '<td style="min-width:140px;">' + opportunity_html + '</td>';
					html += '<td style="min-width:140px;">' + opportunity_html + '</td>';
					html += '<td style="min-width:140px;">' + (row.sla_status || '') + '</td>';
					html += '<td style="min-width:100px;text-align:center;">' + (row.followup_count || 0) + '</td>';
					html += '<td style="min-width:160px;">' + (row.last_followup_at ? frappe.datetime.str_to_user(row.last_followup_at) : '') + '</td>';
					html += '<td style="min-width:160px;">' + (row.next_followup_due ? frappe.datetime.str_to_user(row.next_followup_due) : '') + '</td>';
					// AI Reply column
					html += '<td style="min-width:260px;white-space:normal;">';
					if (row.ai_reply) {
						html += '<div style="background:#f8f9fa;padding:8px;border-radius:6px;margin-bottom:6px;max-height:120px;overflow:auto;">' + $('<div>').text(row.ai_reply).html() + '</div>';
					} else {
						html += '<div style="color:#888;">— No suggestion</div>';
					}
					if (row.handoff_name) {
						html += ' <button class="btn btn-sm btn-outline-secondary generate-reply" data-handoff="' + (row.handoff_name || '') + '">Generate AI Reply</button>';
						html += ' <button class="btn btn-sm btn-outline-primary copy-reply" data-reply="' + (row.ai_reply ? $('<div>').text(row.ai_reply).html() : '') + '">Copy Reply</button>';
					}
					html += '</td>';
					// Next Action column
					html += '<td style="min-width:140px;">' + (row.next_action || row.next_best_action || '') + '</td>';
					// Copilot column (Generate button)
					html += '<td style="min-width:120px;text-align:center;">';
					if (row.handoff_name) {
						html += '<button class="btn btn-sm btn-primary generate-ai" data-handoff="' + (row.handoff_name || '') + '">🤖 Generate</button>';
					} else {
						html += '<span style="color:#999;">—</span>';
					}
					html += '</td>';
					html += '<td style="min-width:260px;white-space:normal;">' + handoff_html + '</td>';
					html += '<td style="min-width:180px;white-space:nowrap;">' + (row.assigned_to || '') + '</td>';
					html += '<td style="min-width:80px;text-align:center;">' + (row.todo_count || 0) + '</td>';
					html += '<td style="min-width:180px;white-space:nowrap;">' + frappe.datetime.str_to_user(row.last_activity || '') + '</td>';
					html += '</tr>';
				});

				html += '</tbody></table>';
				html += '</div>';

				$(page.body).html(html);

				// Filter button behavior
				$(page.body).find('.filter-btn').on('click', function() {
					let filter = $(this).data('filter');
					$('#inbox-table tbody tr').show();
					if (filter === 'all') return;

					// Special filters
					if (filter === 'Open Handoffs') {
						$('#inbox-table tbody tr').each(function() {
							let status = ($(this).attr('data-handoff-status') || '').toLowerCase();
							let name = $(this).attr('data-handoff-name') || '';
							if (!name || status !== 'open') $(this).hide();
						});
						return;
					}

					if (filter === 'Assigned To Me') {
						let me = (frappe.session && frappe.session.user) ? frappe.session.user.toLowerCase() : '';
						$('#inbox-table tbody tr').each(function() {
							let assigned = ($(this).attr('data-handoff-assigned') || '').toLowerCase();
							if (!assigned || assigned.indexOf(me) === -1) $(this).hide();
						});
						return;
					}

					if (filter === 'My Leads') {
						let me = (frappe.session && frappe.session.user) ? frappe.session.user.toLowerCase() : '';
						$('#inbox-table tbody tr').each(function() {
							let assigned = ($(this).attr('data-handoff-assigned') || '').toLowerCase();
							if (!assigned || assigned.indexOf(me) === -1) $(this).hide();
						});
						return;
					}

					// Fallback text search for other filters
					$('#inbox-table tbody tr').each(function() {
						let text = $(this).text().toLowerCase();
						if (text.indexOf((filter || '').toLowerCase()) === -1) $(this).hide();
					});
				});

				$('#inbox-search').on('keyup', function() {
					let value = $(this).val().toLowerCase();
					$('#inbox-table tbody tr').filter(function() {
						$(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
					});
				});

				$(page.body).find('.open-contact').on('click', function(e) {
					e.preventDefault();
					let contact = $(this).data('contact');
					open_timeline(contact);
				});

				// Claim handoff handler
				$(page.body).on('click', '.claim-handoff', function(e) {
					e.preventDefault();
					let handoff = $(this).data('handoff');
					if (!handoff) return;
					frappe.call({
						method: 'ai_sales_agent.ai_sales_agent.utils.claim_engine.claim_handoff',
						args: { handoff_name: handoff },
						callback: function(r) {
							let res = r.message || {};
							if (res.status === 'success') {
								frappe.msgprint({message: 'Lead claimed successfully', indicator: 'green'});
								load_inbox(page);
							} else {
								frappe.msgprint({message: 'Failed to claim lead: ' + (res.message || 'unknown'), indicator: 'red'});
							}
						}
					});
				});

				// Generate AI Reply -> show modal with suggestion and next action
				$(page.body).on('click', '.generate-reply', function(e) {
					e.preventDefault();
					let handoff = $(this).data('handoff');
					if (!handoff) return;
					frappe.call({
						method: 'ai_sales_agent.ai_sales_agent.utils.sales_copilot.refresh_ai_reply',
						args: { handoff_name: handoff },
						callback: function(r) {
							let res = r.message || {};
							let reply = (res.reply || '').toString();
							let action = (res.next_action || res.nextAction || res.next_action) || '';
							if (reply || action) {
								let modal_html = '';
								modal_html += '<div style="max-height:60vh;overflow:auto;">';
								modal_html += '<h4>AI Suggested Reply</h4>';
								modal_html += '<div style="background:#f8f9fa;padding:12px;border-radius:6px;margin-bottom:12px;white-space:pre-wrap;">' + $('<div>').text(reply).html() + '</div>';
								modal_html += '<h5 style="margin-top:6px;">Next Best Action</h5>';
								modal_html += '<div style="padding:8px 0 0 0;font-weight:600;color:#333;">' + $('<div>').text(action).html() + '</div>';
								modal_html += '<div style="margin-top:14px;">';
								modal_html += '<button class="btn btn-primary copy-modal-reply" data-reply="' + $('<div>').text(reply).html() + '">Copy Reply</button> ';
								modal_html += '<button class="btn btn-default refresh-inbox">Refresh Inbox</button> ';
								modal_html += '<button class="btn btn-secondary close-modal">Close</button>';
								modal_html += '</div>';
								modal_html += '</div>';
								frappe.msgprint({ title: 'AI Copilot', message: modal_html, wide: true });

								// bind modal button handlers (use delegated to document)
								$(document).off('click', '.copy-modal-reply').on('click', '.copy-modal-reply', function(ev) {
									ev.preventDefault();
									let text = $(this).data('reply') || '';
									try {
										navigator.clipboard.writeText($('<div>').html(text).text());
										frappe.msgprint({message: 'Reply copied to clipboard', indicator: 'green'});
									} catch (err) {
										frappe.msgprint({message: 'Unable to copy reply', indicator: 'orange'});
									}
								});

								$(document).off('click', '.refresh-inbox').on('click', '.refresh-inbox', function(ev) {
									ev.preventDefault();
									load_inbox(page);
									frappe.hide_msgprint();
								});

								$(document).off('click', '.close-modal').on('click', '.close-modal', function(ev) {
									ev.preventDefault();
									frappe.hide_msgprint();
								});
							} else {
								frappe.msgprint({message: 'Failed to generate AI reply', indicator: 'red'});
							}
						}
					});
				});

				// Copy reply handler
				$(page.body).on('click', '.copy-reply', function(e) {
					e.preventDefault();
					let text = $(this).data('reply') || '';
					if (!text) return;
					try {
						navigator.clipboard.writeText($('<div>').html(text).text());
						frappe.msgprint({message: 'Reply copied to clipboard', indicator: 'green'});
					} catch (err) {
						frappe.msgprint({message: 'Unable to copy reply', indicator: 'orange'});
					}
				});

				// Copilot generate button (compact) - shows suggested reply and next action
				$(page.body).on('click', '.generate-ai', function(e) {
					e.preventDefault();
					let handoff = $(this).data('handoff');
					if (!handoff) return;
					frappe.call({
						method: 'ai_sales_agent.ai_sales_agent.utils.sales_copilot.refresh_ai_reply',
						args: { handoff_name: handoff },
						callback: function(r) {
							let data = r.message || {};
							frappe.msgprint({
								title: 'AI Sales Copilot',
								message: '<b>Suggested Reply</b><hr>' + $('<div>').text(data.reply || '').html() + '<br><br><b>Next Best Action</b><hr>' + $('<div>').text(data.next_action || data.nextAction || data.next_action).html(),
								wide: true
							});
						}
					});
				});
			}
		});
	}


	function open_timeline(contact) {
		frappe.call({
			method: 'ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_contact_timeline',
			args: { contact: contact },
			callback: function(r) {
				let rows = r.message || [];
				let html = '<h3>' + contact + '</h3><hr>';
				rows.forEach(row => {
					html += '<div style="border:1px solid #ddd;padding:10px;margin-bottom:10px;border-radius:8px;">';
					html += '<b>' + (row.channel || '') + '</b><br><br>' + (row.message || '') + '<hr><small>' + (row.timestamp || '') + '</small>';
					html += '</div>';
				});
				frappe.msgprint({ title: contact, message: html, wide: true });
			}
		});
	}


	function open_workspace(handoff_name) {

		frappe.call({
			method: "ai_sales_agent.ai_sales_agent.page.ai_inbox.ai_inbox.get_workspace_data",
			args: { handoff_name: handoff_name },
			callback: function(r) {
						console.log("WORKSPACE DATA", r.message);
						let d = r.message || {};

						let html = `
					<div style="padding:15px">

						<h3>Customer Profile</h3>

						<p><b>Contact:</b> ${d.handoff.contact || "-"}</p>
						<p><b>Channel:</b> ${d.handoff.channel || "-"}</p>
						<p><b>Lead Category:</b> ${d.handoff.created_from_category || "-"}</p>
						<p><b>Intent:</b> ${d.handoff.created_from_intent || "-"}</p>

						<hr>

						<h3>Opportunity</h3>

						<p><b>Opportunity:</b> ${d.handoff.opportunity || "-"}</p>

						<hr>

						<h3>AI Sales Copilot</h3>

						<p>
							<b>Next Action:</b>
							<span id="copilot_next_action">${d.copilot && d.copilot.action ? d.copilot.action : "-"}</span>
						</p>

						<textarea
							id="copilot_reply"
							style="width:100%;height:120px"
						>
${d.copilot && d.copilot.reply ? d.copilot.reply : ""}
						</textarea>

						<div style="margin-top:10px">

							<button class="btn btn-primary" id="send_copilot_reply">Send Reply</button>
							<button class="btn btn-secondary" id="regenerate_copilot_reply" style="margin-left:8px;">Regenerate AI Reply</button>
							<button class="btn btn-outline-primary" id="claim_workspace_handoff" style="margin-left:8px;">📌 Claim Lead</button>

							<button class="btn btn-outline-secondary" id="close_workspace_handoff" style="margin-left:8px;">Close Handoff</button>

						</div>

						<hr>

						<h3>Timeline</h3>

						<div id="timeline_container"></div>

						<hr>

						<h3>Sales Operations</h3>

						<p><b>SLA:</b> ${d.handoff.sla_status || ""}</p>
						<p><b>Followups:</b> ${d.handoff.followup_count || 0}</p>
						<p><b>Open Tasks:</b> ${Array.isArray(d.todos) ? d.todos.length : 0}</p>

					</div>
					`;

					let timeline_html = "";
					(d.timeline || []).forEach(row => {
						timeline_html += `
							<div style="border-bottom:1px solid #ddd;padding:8px;">

								<b>${row.channel || ''}</b>

								(${row.direction || ''})

								<br>

								${row.message || ''}

							</div>
						`;
					});

					html = html.replace('<div id="timeline_container"></div>', `<div>${timeline_html}</div>`);

					let dialog = new frappe.ui.Dialog({
						title: "Unified Workspace",
						size: "extra-large",
						fields: [
							{ fieldtype: "HTML", fieldname: "workspace" }
						]
					});

					dialog.show();
					dialog.fields_dict.workspace.$wrapper.html(html);

					// Wire Send button to reply_dispatcher.send_reply and refresh workspace on success
					$(document).off("click", "#send_copilot_reply");
					$(document).on("click", "#send_copilot_reply", function() {

						let reply = $("#copilot_reply").val();

						frappe.call({
							method: "ai_sales_agent.ai_sales_agent.utils.reply_dispatcher.send_reply",
							args: {
								channel: d.handoff.channel,
								contact: d.handoff.contact,
								message: reply,
								handoff_name: d.handoff.name
							},
							callback: function(r) {

								frappe.show_alert({ message: "Reply Sent", indicator: "green" });
								console.log(r.message);
								// Reload workspace to refresh timeline, followups and SLA
								open_workspace(d.handoff.name);
							}
						});

					});

					// Regenerate AI Reply -> call sales_copilot.refresh_ai_reply and update UI in-place
					$(document).off("click", "#regenerate_copilot_reply");
					$(document).on("click", "#regenerate_copilot_reply", function() {

						// disable button briefly
						$('#regenerate_copilot_reply').prop('disabled', true).text('Regenerating...');

						frappe.call({
							method: "ai_sales_agent.ai_sales_agent.utils.sales_copilot.refresh_ai_reply",
							args: { handoff_name: d.handoff.name },
							callback: function(r) {
								let res = r.message || {};
								let reply = (res.reply || '');
								let action = (res.next_action || res.nextAction || res.next_action || '');
								// update textarea and next action
								$('#copilot_reply').val(reply);
								$('#copilot_next_action').text(action || '-');
								frappe.show_alert({ message: 'AI Reply Regenerated', indicator: 'blue' });
								$('#regenerate_copilot_reply').prop('disabled', false).text('Regenerate AI Reply');
							}
						});

					});

					// Claim Lead button: call claim_engine.claim_handoff and refresh workspace
					$(document).off("click", "#claim_workspace_handoff");
					$(document).on("click", "#claim_workspace_handoff", function() {

						let handoff_name = d.handoff && d.handoff.name;
						if (!handoff_name) return;

						frappe.call({
							method: 'ai_sales_agent.ai_sales_agent.utils.claim_engine.claim_handoff',
							args: { handoff_name: handoff_name },
							callback: function(r) {
								let res = r.message || {};
								if (res.status === 'success') {
									frappe.show_alert({ message: 'Lead claimed', indicator: 'green' });
									open_workspace(handoff_name);
								} else {
									frappe.msgprint({ message: 'Failed to claim lead: ' + (res.message || 'unknown'), indicator: 'red' });
								}
							}
						});

					});

					// Close Handoff button: show modal to pick outcome and optional note
					$(document).off("click", "#close_workspace_handoff");
					$(document).on("click", "#close_workspace_handoff", function() {

						let handoff_name = d.handoff && d.handoff.name;
						if (!handoff_name) return;

						let modal = `
							<div>
								<h4>Close Handoff</h4>
								<p>Select outcome and add optional closing note.</p>
								<div style="margin-top:8px;">
									<select id="close_outcome" class="form-control">
										<option value="Closed Won">Closed Won</option>
										<option value="Closed Lost">Closed Lost</option>
										<option value="Closed">Closed</option>
									</select>
								</div>
								<div style="margin-top:8px;">
									<textarea id="close_note" class="form-control" placeholder="Closing notes (optional)"></textarea>
								</div>
								<div style="margin-top:10px;"> 
									<button class="btn btn-primary" id="confirm_close_handoff">Close Handoff</button>
									<button class="btn btn-secondary close-close-modal" style="margin-left:8px;">Cancel</button>
								</div>
							</div>
						`;

						frappe.msgprint({ title: 'Close Handoff', message: modal, wide: true });

						$(document).off('click', '#confirm_close_handoff').on('click', '#confirm_close_handoff', function(ev) {
							ev.preventDefault();
							let outcome = $('#close_outcome').val();
							let note = $('#close_note').val();

							frappe.call({
								method: 'ai_sales_agent.ai_sales_agent.utils.claim_engine.close_handoff',
								args: { handoff_name: handoff_name, outcome: outcome, note: note },
								callback: function(r) {
									let res = r.message || {};
									if (res.status === 'success') {
										frappe.show_alert({ message: 'Handoff closed', indicator: 'green' });
										open_workspace(handoff_name);
									} else {
										frappe.msgprint({ message: 'Failed to close handoff: ' + (res.message || 'unknown'), indicator: 'red' });
									}
								}
							});
						});

						$(document).off('click', '.close-close-modal').on('click', '.close-close-modal', function(ev) {
							ev.preventDefault();
							frappe.hide_msgprint();
						});

					});
			}
		});

	}

