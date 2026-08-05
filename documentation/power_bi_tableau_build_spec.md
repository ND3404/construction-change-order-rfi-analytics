# Power BI and Tableau Build Specification

## Project

**Construction Change Order and RFI Analytics**  
**Subtitle:** Root-Cause, Cycle-Time, and Impact Analysis for Construction Decision Workflows

## Purpose

Create interactive executive and operational dashboards that explain portfolio workflow health, RFI response performance, change-order approval and commercial exposure, workflow bottlenecks, RFI-to-change conversion, operating-segment differences, and project-level priorities.

## Recommended data model

### Dimensions

- `Dim_Project`
- `Dim_Date`
- `Dim_Discipline`
- `Dim_RFI_Type`
- `Dim_Change_Category`
- `Dim_Role`
- `Dim_Status`

### Facts

- `Fact_RFI`
- `Fact_Change_Order`
- `Fact_Workflow_Event`
- `Bridge_RFI_Change`

```text
Dim_Project 1 ─── * Fact_RFI
Dim_Project 1 ─── * Fact_Change_Order
Dim_Project 1 ─── * Fact_Workflow_Event
Fact_RFI 1 ─── * Bridge_RFI_Change
Fact_Change_Order 1 ─── * Bridge_RFI_Change
```

Do not join RFIs directly to change orders without the bridge table because direct joins can multiply records and overstate values.

## Page 1 — Executive Workflow Command Center

### KPI cards

- Projects
- RFIs
- Average RFI Response Days
- RFI On-Time Rate
- Approved Change Value
- Pending Change Exposure
- Average Change Approval Days
- RFI-to-Change Conversion Rate

### Visuals

1. Project health distribution
2. Approved value and pending exposure by change category
3. Top five workflow-risk projects
4. Executive findings narrative
5. Portfolio filters

### Filters

- Project type
- Delivery method
- Project status
- Current phase
- Complexity
- Digital coordination level
- Owner decision profile
- Region

## Page 2 — RFI Performance and Root Causes

- Average response days by discipline
- On-time response rate by discipline
- Cost impact by RFI type
- Schedule impact by RFI type
- Overdue open RFIs by priority
- RFI-to-change conversion by RFI type
- Project-level RFI response scatterplot

## Page 3 — Change Order Commercial Exposure

- Approved value by change category
- Pending exposure by change category
- Approval-cycle distribution
- Approval cycle by initiating party
- Old pending changes over 35 days
- Forecast-incorporation lag
- Approved changes not incorporated
- Schedule-impact days by category

## Page 4 — Workflow Bottlenecks

- Total stage days by status and assigned role
- Average stage duration by status
- Handoff count by role
- Revision-loop count
- RFI Returned for Clarification detail
- Change Returned for Revision detail
- Process funnel from submission to final disposition

Display volume and duration together so that high-volume stages are not mistaken automatically for slow stages.

## Page 5 — Project Priority and Management Review

- Workflow risk score
- Red/Yellow/Green health
- Average RFI response
- Average approval cycle
- Pending exposure as percentage of budget
- Overdue open rate
- High/Critical overdue rate
- Forecast-incorporation lag
- Top 10 project priority table

### Transparent risk logic

Each indicator receives 0 points when Green, 1 point when Yellow, and 2 points when Red.

- Green: 0–2 points
- Yellow: 3–5 points
- Red: 6 or more points

## Page 6 — Statistical and Model Evidence

- Correlation summary
- Project average RFI response vs average approval-cycle scatterplot
- RFI revisions vs response time
- Change revisions vs approval cycle
- Exploratory model AUC comparison
- Model governance warning

The exploratory conversion models are diagnostic only and are not approved for production use.

## Power BI measure examples

```DAX
RFI Count =
COUNTROWS(Fact_RFI)

Average RFI Response Days =
AVERAGE(Fact_RFI[Final_Response_Days])

Responded RFI Count =
CALCULATE([RFI Count], NOT ISBLANK(Fact_RFI[Final_Response_Date]))

On-Time RFI Count =
CALCULATE([RFI Count], Fact_RFI[Response_Compliance_Status] = "On Time")

RFI On-Time Rate =
DIVIDE([On-Time RFI Count], [Responded RFI Count])

Approved Change Value =
CALCULATE(
    SUM(Fact_Change_Order[Approved_Value]),
    Fact_Change_Order[Change_Status] = "Approved"
)

Pending Change Exposure =
CALCULATE(
    SUMX(Fact_Change_Order, ABS(Fact_Change_Order[Submitted_Value])),
    Fact_Change_Order[Change_Status] IN {"Submitted", "Under Review", "Pending"}
)

Average Approval Cycle Days =
CALCULATE(
    AVERAGE(Fact_Change_Order[Approval_Cycle_Days]),
    Fact_Change_Order[Change_Status] = "Approved"
)

RFI-to-Change Conversion Rate =
DIVIDE(
    CALCULATE(DISTINCTCOUNT(Bridge_RFI_Change[RFI_ID])),
    DISTINCTCOUNT(Fact_RFI[RFI_ID])
)
```

## Tableau calculated-field examples

```text
RFI On-Time Rate
SUM(IIF([Response Compliance Status] = "On Time", 1, 0))
/
SUM(IIF(NOT ISNULL([Final Response Date]), 1, 0))

Pending Change Exposure
SUM(
    IIF(
        [Change Status] = "Submitted"
        OR [Change Status] = "Under Review"
        OR [Change Status] = "Pending",
        ABS([Submitted Value]),
        0
    )
)

RFI-to-Change Conversion Rate
COUNTD([Linked RFI ID]) / COUNTD([RFI ID])
```

## Tableau AI demonstration — optional

Where available in the selected Tableau environment, demonstrate AI-assisted analysis with prompts such as:

- Which disciplines have the longest average RFI response time?
- Show change categories with both high approved value and high pending exposure.
- Which projects have high RFI delay and high change approval cycle?
- Summarize the major workflow bottlenecks.
- Explain why the Red-project count is elevated.

Verify product availability and governance settings before relying on AI-assisted features. The published portfolio must remain understandable without the AI layer.

## Design system

- Deep navy: `#071A2C`
- Blue: `#155F86`
- Cyan: `#1EA7C5`
- Light cyan: `#DDF3F8`
- Red status: `#FCE2E0`
- Yellow status: `#FFF2CC`
- Green status: `#DDEFE2`

## Accessibility

- Do not communicate health through color alone.
- Include status text and icons.
- Maintain high contrast.
- Use descriptive titles and alt text.
- Use consistent number formats.
- Provide methodology and limitations pages.

## Validation requirements

1. Reconcile Power BI and Tableau KPI totals to the Excel dashboard.
2. Confirm 3,318 RFIs and 1,119 change orders.
3. Confirm approved change value of approximately $204.57 million.
4. Confirm pending exposure of approximately $88.10 million.
5. Confirm 29 Red, 48 Yellow, and 13 Green projects.
6. Test filters and cross-highlighting.
7. Confirm no many-to-many duplication of approved values.
8. Retain the synthetic-data disclosure.
9. Do not claim causation from correlation.
10. Label the exploratory models as non-production.
