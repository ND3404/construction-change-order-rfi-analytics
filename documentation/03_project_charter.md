# Project Charter

## Project

Construction Change Order and RFI Analytics

## Purpose

Develop a reproducible construction workflow-analytics case study that identifies root causes, bottlenecks, aging, and cost/schedule impacts across change-order and RFI processes.

## Sponsor

In Project LLC

## Project manager and analyst

Narciso M. Dickson

## Business objective

Improve management visibility into change and RFI workflow performance by identifying the projects, categories, disciplines, stages, and conditions associated with the greatest decision delay and commercial exposure.

## Analytical objective

Create a relational dataset and analytical model that measures:

- workflow volume;
- response and approval cycle time;
- aging;
- status transitions;
- revisions and reopen activity;
- cost and schedule impacts;
- RFI-to-change conversion;
- and project-level workflow health.

## Major deliverables

1. Synthetic relational data
2. Data dictionary
3. Cleaning and validation package
4. SQL database and analytical views
5. Excel analysis workbook
6. Power BI dashboard
7. Tableau dashboard
8. Root-cause and workflow findings
9. Management action plan
10. GitHub and portfolio publication
11. Final report

## High-level schedule

| Phase | Planned outcome |
|---|---|
| Ask | Approved charter, business questions, KPI framework, methodology |
| Prepare | Raw synthetic data, data model, dictionary, quality rules |
| Process | Clean data, validation, SQLite database, cleaning log |
| Analyze | Metrics, comparisons, relationships, prioritization |
| Share | Dashboards, narrative, GitHub-ready communication |
| Act | Recommendations, controls, roadmap, monitoring plan |

## Assumptions

- Synthetic data will be used.
- The project will not make legal or contractual-entitlement determinations.
- Final thresholds are portfolio assumptions.
- The workflow-event table will support cycle-time and bottleneck analysis.
- RFI and change-order links will be explicitly represented rather than inferred only from text.

## Constraints

- No access to actual construction client systems
- No verified industry benchmark dataset
- No direct production connector in the initial project
- Limited ability to represent every contractual workflow variation
- Public-facing outputs must remain understandable to recruiters and clients

## Principal risks

| Risk | Response |
|---|---|
| Synthetic patterns appear too artificial | Use realistic variation, overlap, missingness, and exceptions |
| Metrics imply causation | Use association language and limitations |
| Dataset becomes unnecessarily complex | Preserve a clear table grain and documented keys |
| Project duplicates Project 1 | Focus on workflow events, cycle time, bottlenecks, and RFI-to-change conversion |
| Dashboard becomes crowded | Separate executive and operational views |
| Public users misunderstand the data | Repeat synthetic-data disclosure |
