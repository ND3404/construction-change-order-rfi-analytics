# Cleaning and Validation Methodology

## Layered architecture

```text
Raw synthetic CSVs
        ↓
Deterministic cleaning and validation script
        ↓
Clean relational CSVs
        ↓
SQLite clean tables and analytical views
        ↓
Analyze phase
```

## Core principles

1. Preserve the raw layer unchanged.
2. Remove exact duplicates while retaining one canonical row.
3. Use controlled-value mappings for abbreviations, case variants, and synonymous labels.
4. Repair missing or invalid fields only from unambiguous evidence.
5. Quarantine invalid parent relationships rather than guessing.
6. Cascade referential-integrity quarantine to dependent orphan records.
7. Maintain a field-level audit trail.
8. Reconcile raw, removed, quarantined, and clean row counts.
9. Validate the clean files independently of the known-issue register.
10. Enforce relational integrity in SQLite.

## Sequence normalization

The raw workflow data contained open items where generated event sequence values did not follow chronological timestamps. The Process phase detected these conditions through validation rather than relying only on the known-issue register.

For each affected item:

- event timestamps were preserved;
- events were ordered by timestamp;
- `Event_Sequence` was renumbered from 1 through the final event;
- every changed sequence was recorded in the cleaning log.

This treatment preserves observed timing while restoring a technically valid ordered event stream.

## Null handling

- Blank final dates are retained for genuinely open items.
- Final dates are required for Answered and Closed RFIs.
- Approved date and approved value are required for Approved changes.
- Optional commercial values remain null when the lifecycle has not reached that stage.
- Missing roles are set to `Unknown` only when evidence-based inference is not possible.

## Date handling

Dates use ISO `YYYY-MM-DD`. Event timestamps use ISO date-time values. The observed workflow-event cutoff is December 31, 2025. Forecast dates may extend beyond the observation cutoff.

## Numerical conventions

- Project budgets and contingency are nonnegative.
- RFI impact amounts use positive exposure values.
- Change-order values may be negative for deductive changes.
- Requested and approved schedule days represent nonnegative extension days.
- Ratings are whole numbers from 1 through 5.

## Reproducibility

Run:

```powershell
python data\processing\process_clean_and_validate.py
```

The pipeline recreates the clean files, processed technical table, SQLite database, SQL scripts, cleaning log, quarantine register, quality results, row reconciliation, and validation report.
