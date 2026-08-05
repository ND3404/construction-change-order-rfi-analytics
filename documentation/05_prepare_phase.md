# Prepare Phase

## Project

**Construction Change Order and RFI Analytics**  
**Root-Cause, Cycle-Time, and Impact Analysis for Construction Decision Workflows**

**Project code:** IP-DA-002  
**Sponsor:** In Project LLC

## Phase objective

The Prepare phase establishes the synthetic data strategy, relational structure, table grain, controlled values, data dictionary, generation logic, raw-file preservation rules, and quality-validation plan required for the later Process and Analyze phases.

## Professional lifecycle terminology

Within the primary six-phase lifecycle, this phase is called **Prepare**.

Related professional terminology includes:

| Framework | Closely aligned terminology |
|---|---|
| Google Data Analytics | Prepare |
| CRISP-DM | Data Understanding |
| DMAIC | Measure |
| Microsoft Data Science Lifecycle | Data Acquisition and Understanding |
| PMI project governance | Planning |

These terms are conceptually aligned but are not treated as exact equivalents.

## Synthetic-data decision

A synthetic relational dataset was selected because complete public construction datasets rarely combine:

- project attributes;
- detailed RFI lifecycle dates;
- detailed change-order lifecycle dates;
- workflow status transitions and handoffs;
- cost and schedule impacts;
- forecast-incorporation dates;
- and explicit RFI-to-change-order relationships.

All records are fictional. The dataset is intended for education, portfolio demonstration, analytical methodology, dashboard development, and future predictive-model experimentation.

## Dataset scope

| Table | Intended unique records | Raw records after controlled quality injections |
|---|---:|---:|
| Projects | 90 | 92 |
| RFI Log | 3,320 | 3,328 |
| Change Orders | 1,120 | 1,125 |
| Workflow Events | 11,298 | 11,308 |
| RFI Change Links | 680 | 683 |
| **Total** | **16,508** | **16,536** |

**Generation seed:** 20260803  
**Observed-data cutoff:** 2025-12-31  
**Primary date range:** 2022–2025

## Relational structure

```text
Projects
  ├──< RFI Log
  ├──< Change Orders
  ├──< Workflow Events
  └──< RFI Change Links

RFI Log >──< Change Orders
       through RFI Change Links

Workflow Events
  ├── Item_Type = RFI        → Item_ID references RFI_ID
  └── Item_Type = Change Order → Item_ID references Change_Order_ID
```

## Table grain

| Table | Grain |
|---|---|
| Projects | One row per construction project |
| RFI Log | One row per RFI |
| Change Orders | One row per change item |
| Workflow Events | One row per workflow status transition or handoff |
| RFI Change Links | One row per explicit RFI-to-change-order relationship |

## Files generated

### Raw data

- `data/raw/projects_raw.csv`
- `data/raw/rfi_log_raw.csv`
- `data/raw/change_orders_raw.csv`
- `data/raw/workflow_events_raw.csv`
- `data/raw/rfi_change_links_raw.csv`

### Reproducibility

- `data/generation/generate_synthetic_change_rfi_data.py`

### Documentation

- `documentation/construction_change_order_rfi_data_dictionary.xlsx`
- `documentation/05_prepare_phase.md`
- `documentation/06_dataset_methodology.md`
- `documentation/07_data_quality_rules.md`
- `documentation/08_relationship_model.md`
- `documentation/known_raw_data_quality_issues.csv`
- `documentation/raw_dataset_profile.json`
- `documentation/raw_dataset_profile.md`
- `documentation/prepare_phase_manifest.json`

## Known raw-data quality injections

The raw files intentionally contain documented quality issues for the Process phase.

| Issue type | Count |
|---|---:|
| Categorical standardization | 35 |
| Exact duplicate | 28 |
| Invalid date sequence | 9 |
| Invalid foreign key | 7 |
| Invalid numeric value | 5 |
| Missing critical value | 10 |
| Missing value | 3 |

**Total documented issues:** 97

The injected issues include:

- exact duplicates;
- categorical variants;
- missing critical values;
- invalid date sequences;
- invalid numerical values;
- invalid foreign keys;
- and missing workflow-role values.

The issue register identifies the affected record, field, issue, and expected Process-phase treatment.

## Raw-data governance

1. Raw CSV files are immutable analytical source records.
2. Cleaning will occur only in `data/cleaned/` and `data/processed/`.
3. Invalid parent relationships will be quarantined rather than guessed.
4. Missing values will be reconstructed only when supporting workflow evidence is unambiguous.
5. Every transformation will be recorded in the cleaning log.
6. Primary-key and foreign-key integrity will be tested after cleaning.
7. Raw and cleaned row counts will be reconciled.

## Prepare-phase validation

The following checks were completed:

- all five raw files were generated;
- intended unique counts fall within the Ask-phase scope;
- every table contains the documented columns;
- deterministic generation is available through the saved script and seed;
- observed workflow-event dates do not exceed the data cutoff;
- explicit relationship keys are present;
- known quality issues are registered;
- no actual client, employee, contract, address, or confidential record is present;
- and Project 2 files remain isolated from Project 1.

## Limitations

- The dataset is synthetic and is not an industry benchmark.
- Workflow structures are simplified representations of common construction processes.
- Legal entitlement, contract interpretation, claims validity, and responsibility allocation are outside scope.
- Relationships embedded in the data are designed for analytical learning and do not prove real-world causality.
- Some open records have required dates beyond the cutoff, which is valid because they were submitted near the end of the observation period.
- Forecast dates may extend beyond the observed-data cutoff.

## Phase gate decision

**Prepare phase status: Complete**

Proceed to the Process phase to profile, clean, standardize, validate, quarantine invalid records, build the SQLite database, and document every transformation.
