# Analyze Phase

## Project

**Construction Change Order and RFI Analytics**  
**Project code:** IP-DA-002  
**Sponsor:** In Project LLC

## Phase objective

The Analyze phase converted the validated clean data into business metrics, workflow diagnostics, project priorities, statistical associations, and exploratory model evidence.

## Professional lifecycle terminology

| Framework | Closely aligned terminology |
|---|---|
| Google Data Analytics | Analyze |
| CRISP-DM | Modeling and Evaluation |
| DMAIC | Analyze |
| Microsoft Data Science Lifecycle | Modeling |
| PMI project governance | Executing; Monitoring and Controlling |

The crosswalk supports professional communication but does not treat the frameworks as identical.

## Portfolio summary

### RFI performance

- RFIs: **3,318**
- Responded RFIs: **3,019**
- Average response: **12.21 days**
- Median response: **10 days**
- On-time response rate: **45.7%**
- Open RFIs: **299**
- Overdue open RFIs: **295**
- RFIs linked to a change: **569 (17.1%)**
- Actual RFI cost impact: **$29,608,500**
- Actual RFI schedule impact: **2,572 days**

### Change-order performance

- Change orders: **1,119**
- Approved: **706**
- Pending workflow: **221**
- Approved value: **$204,568,300**
- Pending absolute exposure: **$88,104,000**
- Average approval cycle: **28.91 days**
- Median approval cycle: **25 days**
- Old pending changes over 35 days: **219**
- Average forecast incorporation lag: **6.58 days**
- Approved changes not observed as incorporated: **56**

## Principal findings

### 1. Decision speed is a cross-workflow condition

Projects with a **Slow** owner decision profile averaged:

- **16.45 days** for RFI response;
- **26.3%** on-time RFI performance;
- and **37.98 days** for change approval.

Projects with a **Fast** profile averaged:

- **10.40 days** for RFI response;
- **52.8%** on-time performance;
- and **24.36 days** for change approval.

This is an association within the synthetic portfolio, not a causal industry benchmark.

### 2. Digital coordination is associated with RFI performance

High digital-coordination projects averaged **9.55 days** per RFI response and **62.0%** on-time performance. Low digital-coordination projects averaged **14.39 days** and **33.6%** on-time performance.

### 3. Coordination conflict is the largest RFI impact category

Coordination Conflict RFIs generated:

- **$8,225,100** of actual cost impact;
- **533** schedule-impact days;
- and **18.9%** RFI-to-change linkage.

### 4. Three change categories dominate approved value

- Owner-Directed Change: **$44,093,100**
- Design Error or Omission: **$40,302,400**
- Unforeseen Condition: **$39,882,000**

Together they represent **$124,277,500** of approved value.

### 5. Revision loops are important delay signals

- RFI revision count vs response time: **Spearman ρ = 0.432**
- Change revision count vs approval time: **Spearman ρ = 0.468**

The workflow event table also records **512** change-order return-for-revision events and substantial RFI clarification-return volume.

### 6. The strongest tested relationship is cross-process

Project average RFI response time and average change approval cycle have:

- **Pearson r = 0.817**
- **R² = 0.668**
- **Spearman ρ = 0.804**

This suggests that project-level decision and coordination conditions affect both workflows. It does not establish causality.

### 7. Submission-only conversion prediction is insufficient

The submission-only exploratory model achieved a mean cross-validated AUC of **0.510**, approximately chance performance. Adding post-submission response, revision, quality, and impact indicators improved mean AUC to **0.631**, but the result remains diagnostic rather than production-ready.

## Project workflow health

The cumulative trigger model produced:

- Red: **29**
- Yellow: **48**
- Green: **13**

The model uses seven transparent indicators. Each indicator receives:

- 0 points when Green;
- 1 point when Yellow;
- 2 points when Red.

Overall classification:

- Green: 0–2 points
- Yellow: 3–5 points
- Red: 6 or more points

This refinement avoids classifying an entire project Red because of one isolated old item while preserving individual KPI alerts.

## Top management priorities

1. **PRJ-006 — Summit Corporate Center**: score 10; RFI response 11.5 days; change approval 32.5 days; pending exposure 2.66% of budget.
2. **PRJ-025 — Canyon Transit-Oriented Development**: score 9; RFI response 17.0 days; change approval 51.0 days; pending exposure 2.95% of budget.
3. **PRJ-075 — Summit Urban Village**: score 9; RFI response 18.6 days; change approval 43.6 days; pending exposure 1.40% of budget.

## Limitations

- All data is synthetic.
- Thresholds are portfolio assumptions, not universal construction standards.
- The old open-item backlog is intentionally severe in parts of the synthetic dataset.
- Correlations and group differences do not establish causation.
- The exploratory logistic models are not approved for production decisions.
- Some diagnostic features occur after RFI submission and cannot be treated as early-only predictors.
- Project-level aggregation can obscure item-level variation.

## Analyze deliverables

- `analysis/excel/construction_change_order_rfi_analysis.xlsx`
- `analysis/tables/*.csv`
- `sql/04_analysis_queries.sql`
- `documentation/11_analyze_phase.md`
- `documentation/12_metric_definitions.md`
- `documentation/13_statistical_analysis.md`
- `documentation/14_analyze_phase_gate.md`
- `documentation/analyze_validation_summary.json`

## Phase gate decision

**Analyze phase status: Complete**

Proceed to the Share phase to build the executive and operational dashboards, Tableau and Power BI specifications, portfolio narrative, and public GitHub communication.
