# Act Phase

## Project

**Construction Change Order and RFI Analytics**  
**Project code:** IP-DA-002  
**Sponsor:** In Project LLC

## Phase objective

The Act phase converts the validated findings into an implementation-ready management operating plan. It defines priorities, accountable roles, governance cadence, performance targets, control standards, alert conditions, and benefits measurement.

## Professional lifecycle terminology

| Framework | Closely aligned terminology |
|---|---|
| Google Data Analytics | Act |
| CRISP-DM | Deployment |
| DMAIC | Improve and Control |
| Microsoft Data Science Lifecycle | Deployment and Customer Acceptance |
| PMI project governance | Executing; Monitoring and Controlling; transition; Closing |

The frameworks are conceptually aligned but are not treated as identical.

## Management priorities

1. Stabilize Red-project exceptions.
2. Resolve High/Critical overdue RFIs.
3. Reduce old pending changes and pending commercial exposure.
4. Improve owner and design decision cadence.
5. Incorporate approved changes into forecasts promptly.
6. Reduce revision loops through submission and commercial-package quality gates.
7. Use digital coordination pilots on Low-maturity projects.
8. Automate exception identification after governance approval.
9. Measure benefits against the validated baseline.
10. Keep the exploratory model out of production until stronger evidence exists.

## Baseline and 90-day targets

| Measure | Baseline | 90-day target |
|---|---:|---:|
| RFI on-time rate | 45.7% | 70.0% |
| Average RFI response | 12.21 days | 10.0 days |
| Average change approval | 28.91 days | 24.0 days |
| Pending change exposure | $88.10M | ≤$66.08M |
| Overdue open RFIs | 295 | ≤148 |
| Forecast incorporation lag | 6.58 days | ≤5.0 days |
| Old pending changes >35 days | 219 | ≤131 |
| Approved changes not incorporated | 56 | ≤10 |
| Red projects | 29 | ≤18 |
| Green projects | 13 | ≥22 |

These targets are proposed case-study objectives and must be validated before real implementation.

## Implementation sequence

### Days 0–30: Stabilize and govern

- Launch top-10 project triage.
- Assign owners to critical exceptions.
- Establish RFI, change, project-health, and forecast-reconciliation forums.
- Validate the current backlog before measuring improvement.
- Publish response and approval standards.

### Days 31–60: Reduce backlog and improve quality

- Run RFI and change backlog sprints.
- Introduce RFI and change-package completeness gates.
- Review coordination-conflict Pareto results.
- Pilot enhanced digital coordination.
- Track revision loops and repeated missed commitments.

### Days 61–90: Standardize and measure

- Embed KPI targets into routine controls reporting.
- Generate automated exception files.
- Close priority-project corrective actions.
- Compare actual results with the baseline.
- Approve the next-quarter improvement backlog.

## Governance principle

Every management forum must produce:

- a decision;
- an accountable owner;
- a due date;
- evidence of completion;
- and escalation when the commitment is missed.

## Act deliverables

- `act/construction_change_order_rfi_act_plan.xlsx`
- `automation/generate_management_alerts.py`
- `automation/run_act_pipeline.ps1`
- `automation/output/management_alerts.csv`
- `automation/output/management_alert_summary.json`
- `documentation/19_act_phase.md`
- `documentation/20_management_recommendations.md`
- `documentation/21_governance_and_controls.md`
- `documentation/22_act_phase_gate.md`

## Phase gate decision

**Act phase status: Complete**
