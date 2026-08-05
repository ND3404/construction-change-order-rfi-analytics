# Cleaned Data

The Process phase created five validated clean CSV files:

- `projects_clean.csv`
- `rfi_log_clean.csv`
- `change_orders_clean.csv`
- `workflow_events_clean.csv`
- `rfi_change_links_clean.csv`

The clean layer contains standardized and repaired records that passed the documented quality rules. Records with unresolved or invalid parent relationships are stored in `documentation/quarantine_records.csv` rather than included in the clean layer.
