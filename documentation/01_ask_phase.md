# Ask Phase

## 1. Project identity

**Title:** Construction Change Order and RFI Analytics  
**Subtitle:** Root-Cause, Cycle-Time, and Impact Analysis for Construction Decision Workflows  
**Project code:** IP-DA-002  
**Sponsor:** In Project LLC

## 2. Business problem

Change orders and RFIs are essential construction controls, but they often pass through multiple parties, revisions, reviews, and approval gates. Delays or weak workflow discipline can result in:

- unresolved design questions;
- delayed field decisions;
- unpriced or unauthorized work;
- forecast uncertainty;
- rework;
- approval backlog;
- cost and schedule exposure;
- disputes over responsibility;
- and poor executive visibility.

The analytical problem is not simply to count RFIs or change orders. The project must determine:

- where the workflows slow down;
- which conditions are associated with greater impact;
- which categories and disciplines dominate exposure;
- how RFIs convert into change orders;
- and which early-warning indicators are useful for management intervention.

## 3. Primary business question

**Which change-order causes and RFI workflow conditions create the greatest cost and schedule exposure, and where should management intervene to improve response and approval performance?**

## 4. Supporting analytical questions

### Change-order questions

1. Which change categories, initiating parties, disciplines, and project phases generate the greatest approved and pending cost exposure?
2. Which categories produce the greatest approved schedule impact?
3. Where are the longest submission-to-approval cycle times?
4. Which approval stages contain the greatest waiting time?
5. How does approval time vary by project type, contract type, delivery method, and project phase?
6. What percentage of submitted value is approved, rejected, pending, or withdrawn?
7. Which projects have the largest concentration of old pending changes?
8. Are late approvals associated with higher cost variance, greater schedule impact, or more revisions?
9. Which items are approved but not incorporated promptly into the project forecast?
10. Which root causes account for the majority of approved cost and schedule impact?

### RFI questions

1. Which disciplines, priorities, phases, and project types have the longest response times?
2. What percentage of RFIs miss the required response date?
3. Which workflow stages create the greatest queue or waiting time?
4. Which RFIs are reopened, revised, or passed through multiple handoffs?
5. Which projects maintain the largest overdue RFI backlog?
6. At what age do RFIs become more likely to create cost or schedule impact?
7. Which priorities receive inconsistent response treatment?
8. Which disciplines have the highest first-pass resolution failure or reopen rate?
9. How does response performance vary by delivery method and current project phase?
10. Which RFIs eventually generate or support a change order?

### Integrated questions

1. What percentage of change orders are linked to one or more RFIs?
2. How long does it take for an RFI to become a submitted or approved change?
3. Which RFI characteristics are associated with later change-order creation?
4. Are projects with slower RFI workflows also experiencing slower change approvals?
5. Which combined indicators provide the earliest warning of commercial or schedule exposure?
6. Which projects, disciplines, and workflow owners require immediate management attention?

## 5. Stakeholders

| Stakeholder | Decision need |
|---|---|
| Executive sponsor | Understand total exposure and approve intervention priorities |
| Project-controls lead | Monitor cycle time, backlog, cost, schedule, and forecast incorporation |
| Change manager / cost manager | Control submission, pricing, negotiation, approval, and forecast updates |
| Design manager | Improve RFI response, coordination, and discipline accountability |
| Project manager | Resolve project-specific bottlenecks and assign corrective actions |
| Scheduler | Understand decision delays and schedule-impact pathways |
| Owner representative | Review approval aging, owner-directed changes, and decision responsibilities |
| Superintendent | Identify field decisions that may affect sequencing or productivity |
| Data analyst | Maintain metric definitions, data quality, reproducibility, and reporting |
| In Project LLC | Demonstrate a repeatable construction workflow-analytics service |

## 6. Scope

### Included

- Construction projects across multiple sectors and U.S. locations
- Change-order lifecycle from identification through final disposition
- RFI lifecycle from submission through final response or closure
- Status-transition event history
- Approval and response cycle times
- Aging and backlog
- Revision and reopen activity
- Cost and schedule impacts
- Change causes and initiating parties
- RFI disciplines, priorities, and responsible roles
- RFI-to-change-order links
- Descriptive, diagnostic, comparative, and relationship analysis
- Executive and operational dashboards
- Management recommendations and action planning

### Excluded

- Actual client records
- Legal entitlement or contract interpretation
- Claims certification
- Safety and quality incidents
- Detailed CPM schedule files
- Labor productivity measurement
- Subcontractor financial condition
- Final production AI deployment
- Industry-wide benchmarking claims

## 7. Planned dataset

The Prepare phase will design and generate a synthetic relational dataset with approximately:

- 90 construction projects;
- 3,000–3,500 RFIs;
- 1,000–1,250 change orders;
- 8,000–12,000 workflow-event records;
- 500–800 RFI-to-change-order links;
- reporting dates primarily between 2022 and 2025.

### Planned tables

1. **Projects**
   - One row per project
   - Project attributes, contract structure, delivery method, dates, budget, phase, and status

2. **RFI Log**
   - One row per RFI
   - Discipline, priority, submission date, required response date, response date, status, impact indicators, and responsible role

3. **Change Orders**
   - One row per change item
   - Cause, source, discipline, dates, submitted value, approved value, schedule impact, status, and forecast incorporation date

4. **Workflow Events**
   - One row per status transition or handoff
   - Item type, item ID, event date, from status, to status, role, and revision number

5. **RFI Change Links**
   - Many-to-many bridge between RFIs and change orders
   - Link type, confidence, and relationship date

## 8. KPI framework

### Change-order KPIs

- Change-order count
- Submitted value
- Approved value
- Pending value
- Rejected or withdrawn value
- Approval rate
- Approval variance
- Approval cycle days
- Pending age
- Revision count
- Schedule-impact days
- Forecast incorporation lag
- Approved value as percentage of project budget
- Old-pending-change concentration
- First-pass approval rate

### RFI KPIs

- RFI count
- Open RFI count
- Average and median response days
- Required-date compliance
- Overdue rate
- Open-item age
- Priority-weighted aging
- Reopen rate
- Revision rate
- First-pass resolution rate
- Impacted RFI rate
- RFI cost impact
- RFI schedule impact
- RFIs per $10 million of project budget

### Integrated KPIs

- RFI-to-change conversion rate
- Average RFI-to-change submission lag
- Average RFI-to-change approval lag
- Linked change value
- Linked schedule-impact days
- Combined workflow risk status
- Bottleneck-stage share
- Queue time versus processing time
- Cross-functional handoff count
- Project workflow-health classification

## 9. Initial operating thresholds

The following are initial case-study assumptions and will be tested during analysis. They are not universal construction standards.

### RFI response thresholds

| Status | Average response | Overdue rate | High/Critical overdue age |
|---|---:|---:|---:|
| Green | ≤10 days | ≤15% | ≤3 days |
| Yellow | >10–15 days | >15–30% | >3–7 days |
| Red | >15 days | >30% | >7 days |

### Change-order thresholds

| Status | Approval cycle | Old pending share | Forecast incorporation lag |
|---|---:|---:|---:|
| Green | ≤20 days | ≤10% | ≤5 business days |
| Yellow | >20–35 days | >10–25% | >5–10 business days |
| Red | >35 days | >25% | >10 business days |

### Integrated escalation examples

A project may be classified Red when any of the following applies:

- old pending change exposure exceeds a defined percentage of project budget;
- High or Critical RFIs remain overdue beyond the Red threshold;
- approved changes are not incorporated into the forecast promptly;
- a workflow stage accumulates a disproportionate queue;
- linked RFI/change impacts exceed established cost or schedule tolerances;
- or multiple Yellow conditions occur simultaneously.

Final thresholds will be documented transparently and validated against the synthetic portfolio distribution.

## 10. Planned analytical methods

- Descriptive statistics
- Aging-bucket analysis
- Cycle-time distributions
- Pareto analysis
- Cohort comparison
- Process and workflow funnel analysis
- Status-transition analysis
- Bottleneck analysis
- Cross-tabulation
- Correlation analysis
- Nonparametric comparison where appropriate
- Logistic regression for RFI-to-change conversion, if the data supports it
- Survival or time-to-event analysis as an optional advanced method
- Transparent project prioritization
- Power BI and Tableau dashboarding

No causal claim will be made from correlation alone.

## 11. Success criteria

The project will be considered successful when it produces:

1. A fully documented synthetic relational dataset
2. Zero unexplained duplicate primary keys
3. Zero unresolved foreign-key violations in the clean data
4. Documented handling for every critical missing value
5. Reconciled Excel, SQL, Power BI, and Tableau totals
6. Clear metric definitions and formulas
7. At least five management-relevant findings
8. At least three tested early-warning relationships
9. A transparent top-risk prioritization method
10. A change and RFI executive dashboard
11. A detailed workflow diagnostic dashboard
12. Actionable recommendations with owners, timing, and success measures
13. A public GitHub repository
14. A portfolio-ready case-study page
15. A final report with synthetic-data and limitation disclosures

## 12. Ethical and professional controls

- All data will be synthetic.
- No actual person, client, company, contract, or project will be represented.
- Relationships will be presented as associations unless causation is independently supported.
- Small groups and incomplete observations will be labeled.
- Project categories will include variation so that no sector or delivery method is predetermined to perform badly.
- Results will be reproducible and traceable to source records.
- Recommendations will be framed as proposed controls, not guaranteed benefits.
- Public materials will avoid confidential, legal, and personally identifiable information.

## 13. Ask-phase decision

Proceed to the Prepare phase and create the synthetic relational dataset, data dictionary, methodology, generation logic, quality rules, and raw data package.
