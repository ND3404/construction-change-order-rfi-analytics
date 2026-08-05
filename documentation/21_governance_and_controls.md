# Governance and Control Framework

## Decision forums

| Forum | Cadence | Accountable role | Principal output |
|---|---|---|---|
| Daily exception check | Daily | Project Controls Lead | Assigned owner and due date |
| RFI coordination huddle | Twice weekly | Design Manager | Resolved or escalated RFIs |
| Change review board | Weekly | Change Manager | Approved, rejected, revised, or escalated changes |
| Project workflow review | Weekly | Project Controls Lead | Updated recovery plans |
| Forecast reconciliation | Weekly | Project Controls Lead | Reconciled cost and schedule forecast |
| Executive steering review | Monthly | Executive Sponsor | Decisions and resources |
| Root-cause review | Monthly | Design Manager | Prevention actions |
| Methods and threshold review | Quarterly | Project Controls Lead | Approved methodology decisions |

## Escalation principles

Escalate when:

- a Critical RFI is more than three days overdue;
- a High/Critical RFI is more than seven days overdue;
- a pending change is older than 35 days;
- pending exposure exceeds 1.5% of project budget;
- an approved change is not incorporated within five business days;
- a project remains Red without an active recovery plan;
- or a critical data-quality check fails.

## Data and analytical controls

1. Preserve raw data separately from cleaned data.
2. Run primary-key, foreign-key, date, numerical, and reconciliation checks.
3. Do not publish dashboards after a critical validation failure.
4. Keep metric definitions and thresholds version-controlled.
5. Document every threshold change.
6. Retain synthetic-data and limitation disclosures.
7. Keep exploratory models out of production without formal validation.

## Benefits governance

The benefits tracker distinguishes:

- baseline;
- 30-day actual;
- 60-day actual;
- 90-day actual;
- target;
- variance;
- owner;
- and evidence.

No benefit should be reported as realized until a reliable measurement exists.
