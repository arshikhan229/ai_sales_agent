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

