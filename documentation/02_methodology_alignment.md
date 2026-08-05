# Professional Lifecycle and Methodology Alignment

## Primary lifecycle used in this project

The project will be organized using the six-phase analytics workflow:

1. Ask
2. Prepare
3. Process
4. Analyze
5. Share
6. Act

This structure is clear for portfolio communication and business analytics. To improve professional credibility, the project documentation also uses terminology from CRISP-DM, DMAIC, the Microsoft Data Science Lifecycle, and PMI Process Groups.

## Important interpretation

The models below are not identical and should not be presented as exact equivalents.

- CRISP-DM is an iterative analytics and data-mining lifecycle.
- DMAIC is a process-improvement framework.
- Microsoft's lifecycle is designed for data-science solutions intended for deployment.
- PMI Process Groups are project-management process groupings, not a simple sequential project lifecycle.

The project uses a crosswalk to show conceptual alignment while preserving the correct terminology of each model.

## Crosswalk

| Project phase | CRISP-DM terminology | DMAIC terminology | Microsoft terminology | PMI governance terminology |
|---|---|---|---|---|
| Ask | Business Understanding | Define | Business Understanding | Initiating; early Planning |
| Prepare | Data Understanding | Measure | Data Acquisition and Understanding | Planning |
| Process | Data Preparation | Measure; early Analyze | Data Acquisition and Understanding | Executing; Monitoring and Controlling |
| Analyze | Modeling; Evaluation | Analyze | Modeling | Executing; Monitoring and Controlling |
| Share | Evaluation | Analyze; Improve design | Customer Acceptance | Monitoring and Controlling; stakeholder engagement |
| Act | Deployment | Improve; Control | Deployment; Customer Acceptance | Executing; Monitoring and Controlling; Closing/transition |

## How the terminology will appear in deliverables

### Ask / Business Understanding / Define

Documentation will include:

- business problem;
- project charter;
- stakeholder needs;
- business and analytical objectives;
- scope and exclusions;
- success criteria;
- risks and assumptions.

### Prepare / Data Understanding / Measure

Documentation will include:

- source strategy;
- relational model;
- data inventory;
- table grain;
- data dictionary;
- operational definitions;
- initial profiling;
- baseline metrics;
- data-quality rules.

### Process / Data Preparation

Documentation will include:

- cleaning;
- transformation;
- standardization;
- missing-value treatment;
- referential-integrity checks;
- event-log construction;
- analytical-table creation;
- audit trail.

### Analyze / Modeling and Evaluation

Documentation will include:

- descriptive analysis;
- cycle-time analysis;
- bottleneck analysis;
- Pareto analysis;
- cohort comparisons;
- correlations;
- optional regression or time-to-event models;
- business validation;
- limitations.

### Share / Evaluation and Customer Acceptance

Documentation will include:

- executive dashboard;
- operational workflow dashboard;
- narrative findings;
- stakeholder interpretation;
- validation against business questions;
- public portfolio communication.

### Act / Deployment, Improve, and Control

Documentation will include:

- recommendations;
- owners;
- implementation roadmap;
- proposed service levels;
- monitoring controls;
- refresh cadence;
- alert logic;
- benefits-measurement plan;
- continuous-improvement loop.

## Iterative operating model

The practical workflow will be iterative:

```text
Business question
        ↓
Data understanding
        ↓
Data preparation
        ↓
Analysis
        ↓
Business validation
        ↓
Return to data or logic when necessary
        ↓
Communication
        ↓
Action and control
        ↓
Monitoring and continuous improvement
```

## Recommended portfolio wording

> **Methodology:** Google Data Analytics six-phase framework—Ask, Prepare, Process, Analyze, Share, and Act—supported by terminology and practices from CRISP-DM, DMAIC, Microsoft’s data-science lifecycle, and PMI project-governance process groups.

## Official reference list

- IBM CRISP-DM overview:
  https://www.ibm.com/docs/en/spss-modeler/18.6.0?topic=dm-crisp-help-overview

- IBM CRISP-DM phases:
  https://www.ibm.com/docs/en/ws-and-kc?topic=modeler-understanding-preparing-data

- Microsoft Data Science Lifecycle:
  https://learn.microsoft.com/en-us/shows/dev-intro-to-data-science/what-is-the-data-science-lifecycle-2-of-28

- ASQ DMAIC:
  https://asq.org/quality-resources/dmaic

- PMI Process Groups:
  https://www.pmi.org/standards/process-groups
