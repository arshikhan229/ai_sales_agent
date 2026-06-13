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


Notes


If you'd like, I can create `CHANGELOG.md` and populate it with commit references and timestamps.
- Enterprise Reporting (v1.4)

Enterprise Reporting
--------------------

This module provides a read-only analytics layer on top of ERPNext and AI Sales Agent data. It uses existing doctypes (`AI Lead`, `AI Handoff`, `CRM Conversation`, `Opportunity`) and exposes KPI/Channel/Agent/SLA metrics via whitelisted APIs and a reporting page.

Key files:
- `ai_sales_agent/reporting/kpi_engine.py` — KPI helper functions
- `ai_sales_agent/reporting/channel_analytics.py` — Channel-level metrics
- `ai_sales_agent/reporting/reporting.py` — Whitelisted dashboard APIs
- `ai_sales_agent/page/ai_reporting/` — Frontend page and JS to render KPIs and charts
