# Processed Analytical Data

## SQLite database

`construction_change_order_rfi_analytics.sqlite`

The database contains five clean relational tables, the cleaning log, quarantine records, and these analytical views:

- `vw_rfi_metrics`
- `vw_change_metrics`
- `vw_workflow_stage_durations`
- `vw_rfi_change_conversion`
- `vw_project_workflow_counts`

## Technical event table

`workflow_event_durations.csv` adds previous-event timestamps, stage durations, handoff indicators, and revision-loop indicators to the clean workflow event stream.

These outputs are ready for the Analyze phase. They should not be described as completed analytical findings until the formal analysis and business validation are performed.
