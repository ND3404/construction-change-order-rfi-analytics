# Statistical Analysis

## Purpose

The statistical work evaluates associations in the synthetic portfolio and tests whether selected indicators are informative. It does not establish real-world causality.

## Association methods

- **Point-biserial correlation:** continuous variable versus binary outcome
- **Spearman correlation:** monotonic association for skewed counts and cycle times
- **Pearson correlation:** linear association at the project-aggregate level
- **Five-fold cross-validated logistic regression:** exploratory RFI-to-change classification

## Principal results

| Relationship | Statistic | Result |
|---|---|---:|
| RFI response vs cost-impact flag | Point-biserial r | 0.289 |
| RFI response vs schedule-impact flag | Point-biserial r | 0.234 |
| RFI response vs linked-to-change flag | Point-biserial r | 0.043 |
| RFI revisions vs response days | Spearman ρ | 0.432 |
| Response quality vs response days | Spearman ρ | -0.510 |
| Change revisions vs approval days | Spearman ρ | 0.468 |
| Change value vs approval days | Spearman ρ | 0.022 |
| Project avg RFI response vs avg approval cycle | Pearson r | 0.817 |
| Project avg RFI response vs avg approval cycle | Spearman ρ | 0.804 |

## Exploratory conversion models

### Submission-only model

Inputs available near RFI submission:

- discipline;
- priority;
- RFI type;
- submitting and responsible roles;
- drawing reference count;
- project type;
- delivery method;
- complexity;
- digital coordination;
- owner decision profile.

**Mean five-fold AUC: 0.510 ± 0.021**

Interpretation: these attributes alone do not discriminate later change linkage in the synthetic portfolio.

### Diagnostic model

Additional inputs:

- response days;
- revision and reopen counts;
- response quality;
- cost and schedule impact flags;
- field-work impact.

**Mean five-fold AUC: 0.631 ± 0.031**

Interpretation: post-submission workflow and impact data improve discrimination, but the result is not strong enough for production decision-making.

## Governance conclusion

The exploratory models should be presented as analytical evidence, not AI deployment. Production use would require:

- a real governed dataset;
- temporal validation;
- leakage controls;
- probability calibration;
- subgroup performance review;
- model monitoring;
- and stakeholder acceptance.
