### Ai Sales Agent

ai sale agent

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app ai_sales_agent
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/ai_sales_agent
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

## Recent Work / Changelog
Summary of recent improvements (v0.9 — stabilization):

This release focuses on improving lead quality, adding a human handoff workflow, and increasing observability in the inbox.

Highlights

- Sales-intent filtering: Heuristics now distinguish sales-focused messages from marketing/newsletter content to reduce false-positive leads.
- Human handoff workflow: Introduced the `AI Handoff` DocType and the `ai_sales_agent.utils.handoff_rules` utility to decide, create, and assign handoffs when human attention is required.
- Pipeline integration: `channel_processor` evaluates `should_handoff()` and creates handoffs with idempotent checks and guarded error handling to avoid duplicates and failures.
- Observability: Added structured audit logging around AI analysis, handoff decisions, and handoff creation to simplify troubleshooting of edge cases.
- Inbox backend & API: `ai_inbox.py` now returns per-row handoff metadata (`handoff_name`, `handoff_status`, `handoff_assigned_to`, `has_handoff`) and aggregate counters for open/total handoffs.
- Inbox UI enhancements: `ai_inbox.js` includes KPI cards, interactive filters (Open Handoffs, Assigned To Me, channel/category), and a responsive handoff column featuring badges and links.
- Developer utility: `debug_inspect_lead(lead_name)` helper available for non-interactive inspection via `bench execute` to reproduce and diagnose problematic leads.

Notes

- Database impact: Adds the `AI Handoff` DocType; no other breaking schema changes expected.
- Suggested next steps: Move this summary into a dedicated `CHANGELOG.md` and annotate entries with commit SHAs and dates for release tracking.

If you'd like, I can create `CHANGELOG.md` and populate it with commit references and timestamps.
