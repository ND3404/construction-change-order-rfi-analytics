# Synthetic Dataset Methodology

## Purpose

This methodology documents how the Project 2 dataset was created and how realistic variation, workflow behavior, analytical relationships, reproducibility, and ethical controls were incorporated.

## Reproducibility

- **Random seed:** 20260803
- **Generation script:** `data/generation/generate_synthetic_change_rfi_data.py`
- **Observed-data cutoff:** 2025-12-31
- **External packages required:** None; the script uses the Python standard library.

Run from the project root:

```powershell
python data\generation\generate_synthetic_change_rfi_data.py
```

The script overwrites the five raw CSV files and the known-issue register using the same deterministic seed.

## Portfolio design

The portfolio contains 90 intended unique fictional construction projects across:

- Residential
- Commercial
- Institutional
- Industrial
- Heavy Civil & Infrastructure
- Mixed-Use

Project attributes include:

- U.S. location;
- client type;
- contract type;
- delivery method;
- complexity level;
- digital coordination level;
- owner decision profile;
- budget and contingency;
- planned and forecast dates;
- status and phase;
- and fictional management-role identifiers.

Project budgets and durations vary by project type, complexity, and random variation. No project type or delivery method is designed to be automatically successful or unsuccessful.

## RFI generation

The RFI Log contains 3,320 intended unique records.

RFI volume is influenced by:

- project size;
- complexity;
- digital coordination;
- and random portfolio variation.

RFI response behavior incorporates:

- discipline;
- priority;
- project complexity;
- owner decision profile;
- digital coordination;
- revision activity;
- and reopen activity.

Impact probability varies with:

- response delay;
- priority;
- RFI type;
- complexity;
- and revision count.

This creates useful analytical relationships while preserving substantial overlap and noise.

## Change-order generation

The Change Orders table contains 1,120 intended unique records.

Change volume is influenced by:

- project scale;
- complexity;
- owner decision profile;
- and random variation.

Approval cycle time incorporates:

- change category;
- project complexity;
- owner decision profile;
- and revision count.

Submitted and approved values vary by:

- project budget;
- change category;
- change type;
- negotiation;
- and random variation.

Approved changes may have a forecast-incorporation date. When incorporation would occur after the observed-data cutoff, the value is left blank to represent an item not yet observed as incorporated.

## Workflow-event generation

The Workflow Events table contains 11,298 intended unique status-transition records.

Each RFI includes:

- submission;
- a current or final response state;
- and a revision-return event when applicable.

Each change order includes:

- identification;
- submission;
- a current or final disposition;
- and a representative return-for-revision event when applicable.

The event table supports:

- stage-duration calculations;
- queue-time analysis;
- handoff analysis;
- revision-loop analysis;
- and bottleneck identification.

## RFI-to-change relationships

The bridge table contains 680 intended unique links.

Plausible relationships are weighted toward RFIs that:

- have cost or schedule impact;
- share a discipline with the change;
- involve coordination, field condition, or missing-information issues;
- and occur within a reasonable time window before change identification.

Every link is explicitly stored. The analysis will not rely only on inference from titles.

## Embedded analytical patterns

The generator creates moderate, noisy relationships suitable for descriptive, diagnostic, and predictive learning:

- longer RFI response times can be associated with impact;
- revisions can lengthen response and approval cycles;
- complexity can increase workflow volume and cycle time;
- better digital coordination can moderate RFI response burden;
- owner decision profile can influence approval timing;
- and RFI characteristics can influence the probability of later linkage to a change order.

These are synthetic design relationships, not claims about actual industry causation.

## Controlled raw-data defects

The generator intentionally adds 97 documented raw-data issues after the valid base records are created.

The purpose is to demonstrate:

- data profiling;
- duplicate removal;
- category standardization;
- evidence-based repair;
- foreign-key quarantine;
- validation;
- and audit-trail documentation.

The Process phase must not silently repair undocumented issues or guess missing parent relationships.

## Bias and ethics controls

- No actual organization or person is represented.
- Project names and IDs are fictional.
- Performance variation exists within every category.
- Category effects are small relative to project-level variation.
- Public reporting must retain the synthetic-data disclosure.
- Association language must be used unless causal evidence exists.
- The analysis must distinguish observed values, calculated metrics, predictions, and recommendations.
