# Act-Phase Automation

## Purpose

The automation package creates management exception files from the validated Project 2 data.

## Files

- `generate_management_alerts.py`
- `run_act_pipeline.ps1`
- `output/management_alerts.csv`
- `output/management_alert_summary.json`

## Alerts

The script creates alerts for:

- Red projects
- Project pending exposure above 1.5% of budget
- High/Critical RFIs overdue more than 7 days
- Overdue RFIs affecting field work
- Pending changes older than 35 days
- Approved changes without an observed forecast incorporation date
- Forecast-incorporation lag above 5 days

## Run locally

From PowerShell:

```powershell
cd "<PROJECT_ROOT>"
powershell -ExecutionPolicy Bypass -File automation\run_act_pipeline.ps1
```

Or run Python directly:

```powershell
python automation\generate_management_alerts.py
```

## Scheduling options

The script may later be scheduled through Windows Task Scheduler, GitHub Actions, an Azure Function, Microsoft Fabric, or another approved orchestration platform. No live recurring schedule is created by this package.

## Governance

- Do not send alerts externally until recipients and suppression rules are approved.
- Do not treat the synthetic thresholds as universal standards.
- Stop publication when critical data-quality checks fail.
- The exploratory RFI-to-change model is excluded from automated production decisions.
