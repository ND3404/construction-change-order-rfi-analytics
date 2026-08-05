# Analyze Metric Definitions

## RFI metrics

| Metric | Definition |
|---|---|
| Final response days | Final response date minus submitted date |
| On-time rate | On-time responded RFIs divided by all responded RFIs |
| Overdue open rate | Open RFIs past required response date divided by all RFIs |
| High/Critical overdue rate | High or Critical overdue open RFIs divided by all RFIs |
| RFI-to-change rate | Unique RFIs linked to at least one change divided by all RFIs |
| Actual RFI cost impact | Sum of actual cost impact recorded on RFI records |
| Actual RFI schedule impact | Sum of actual schedule-impact days recorded on RFI records |

## Change-order metrics

| Metric | Definition |
|---|---|
| Approval cycle days | Approved date minus submitted date |
| Pending exposure | Absolute submitted value for Submitted, Under Review, and Pending changes |
| Old pending change | Pending workflow item older than 35 days at the data cutoff |
| Forecast incorporation lag | Forecast incorporation date minus approved date |
| Approved not incorporated rate | Approved items without an observed forecast incorporation date divided by approved items |
| Linked change | Change order linked to at least one RFI |

## Workflow metrics

| Metric | Definition |
|---|---|
| Stage duration | Current event timestamp minus prior event timestamp for the same item |
| Handoff | Assigned role changes from the prior event |
| Revision loop | Transition reaches Returned for Clarification or Returned for Revision |
| Total stage days | Sum of stage durations for a grouped workflow state and role |
| Bottleneck stage | Stage with high total duration, average duration, volume, or revision-loop activity |

## Project risk points

| Indicator | Green | Yellow: 1 point | Red: 2 points |
|---|---:|---:|---:|
| Average RFI response | ≤10 days | >10–15 | >15 |
| Overdue open rate | ≤15% | >15–30% | >30% |
| High/Critical overdue rate | ≤2% | >2–5% | >5% |
| Average change approval | ≤20 days | >20–35 | >35 |
| Pending exposure / budget | ≤0.5% | >0.5–1.5% | >1.5% |
| Average forecast lag | ≤5 days | >5–10 | >10 |
| Approved not incorporated rate | ≤5% | >5–15% | >15% |

Overall project health:

- Green: 0–2 points
- Yellow: 3–5 points
- Red: 6 or more points

The risk score is transparent, deterministic, and intended for prioritization—not contractual or legal conclusions.
