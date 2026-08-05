# Process Phase

## Project

**Construction Change Order and RFI Analytics**  
**Project code:** IP-DA-002  
**Sponsor:** In Project LLC

## Phase objective

The Process phase converted the immutable raw synthetic records into a clean, validated, traceable relational data layer suitable for SQL, Excel, Power BI, Tableau, workflow analysis, and later predictive experimentation.

## Professional lifecycle terminology

The primary project phase is **Process**. Related terminology includes:

| Framework | Closely aligned terminology |
|---|---|
| Google Data Analytics | Process |
| CRISP-DM | Data Preparation |
| DMAIC | Measure and early Analyze |
| Microsoft Data Science Lifecycle | Data Acquisition and Understanding |
| PMI project governance | Executing; Monitoring and Controlling |

The terms are used as a professional crosswalk and are not presented as identical frameworks.

## Raw-to-clean reconciliation

| Table | Raw | Duplicates removed | Quarantined | Clean |
|---|---:|---:|---:|---:|
| Projects | 92 | 2 | 0 | 90 |
| RFI Log | 3,328 | 8 | 2 | 3,318 |
| Change Orders | 1,125 | 5 | 1 | 1,119 |
| Workflow Events | 11,308 | 10 | 12 | 11,286 |
| RFI Change Links | 683 | 3 | 3 | 677 |
| **Total** | **16,536** | **28** | **18** | **16,490** |

Every table reconciled according to:

```text
Raw rows = Clean rows + Duplicate removals + Quarantined rows
```

## Cleaning and transformation actions

The audit log contains **226 actions**:

- 28 duplicate removals;
- 35 categorical standardizations;
- 10 missing critical-value repairs;
- 9 invalid date-sequence repairs;
- 5 numerical sign corrections;
- 3 missing workflow-role repairs;
- 7 directly identified invalid foreign-key quarantines;
- 11 cascading referential-integrity quarantines;
- and 118 event-sequence normalizations affecting 59 workflow items.

The 118 event actions represent old and new sequence assignments for individual events. Sequence values were changed only when the raw sequence conflicted with chronological timestamps.

## Evidence-based repair rules

### RFI final response dates

Missing or invalid final response dates were reconstructed from the final `Answered` or `Closed` workflow event when the evidence was unambiguous.

### Change approval values

Approved changes missing an approved value were repaired from the final negotiated value only when:

- change status was Approved;
- pricing status was Final;
- and negotiated value was populated.

### Change approval dates

Invalid approval dates were reconstructed from the final `Approved` workflow event. Where an existing close date preceded the repaired approval date, the close date was aligned to the repaired approval date to preserve sequence validity.

### Numerical values

Negative RFI cost impacts and negative requested schedule-extension days were corrected to positive values only where the record’s flags and documented convention supported that treatment.

### Missing workflow roles

Roles were inferred from the item master and controlled workflow transition only when evidence was unambiguous. The process did not use speculative role assignment.

## Quarantine policy

Rows were quarantined when parent relationships could not be trusted without guessing. The quarantine register contains **18 rows**:

- 2 RFIs;
- 1 change order;
- 12 workflow events;
- and 3 RFI/change links.

This includes dependent events and links that became orphaned after their parent item was quarantined.

## Quality validation

The clean dataset passed **22 of 22 checks**:

- five primary-key checks;
- seven foreign-key and polymorphic-parent checks;
- two cross-record consistency checks;
- four date and workflow-sequence checks;
- two completeness checks;
- one numerical validation check;
- and one controlled-value check.

Results:

- unresolved foreign-key violations: **0**;
- failed quality checks: **0**;
- row reconciliation failures: **0**;
- SQLite `PRAGMA foreign_key_check`: no rows;
- SQLite `PRAGMA quick_check`: `ok`.

## Process deliverables

### Clean data

- `data/cleaned/projects_clean.csv`
- `data/cleaned/rfi_log_clean.csv`
- `data/cleaned/change_orders_clean.csv`
- `data/cleaned/workflow_events_clean.csv`
- `data/cleaned/rfi_change_links_clean.csv`

### Processed data

- `data/processed/construction_change_order_rfi_analytics.sqlite`
- `data/processed/workflow_event_durations.csv`

### Reproducible pipeline

- `data/processing/process_clean_and_validate.py`

### SQL

- `sql/01_create_clean_schema.sql`
- `sql/02_create_analysis_views.sql`
- `sql/03_process_validation_queries.sql`

### Audit and validation

- `documentation/construction_change_order_rfi_process_log.xlsx`
- `documentation/cleaning_log.csv`
- `documentation/quarantine_records.csv`
- `documentation/data_quality_results.csv`
- `documentation/row_reconciliation.csv`
- `documentation/process_validation_report.json`

## Phase gate decision

**Process phase status: Complete**

Proceed to the Analyze phase to calculate RFI response, change approval, aging, conversion, impact, workflow bottleneck, project-comparison, and early-warning metrics.
