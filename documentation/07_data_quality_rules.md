# Data Quality Rules

## Purpose

These rules define the tests that will be applied in the Process phase.

## Primary-key rules

| Rule ID | Table | Rule |
|---|---|---|
| PK-01 | Projects | Project_ID must be nonblank and unique |
| PK-02 | RFI Log | RFI_ID must be nonblank and unique |
| PK-03 | Change Orders | Change_Order_ID must be nonblank and unique |
| PK-04 | Workflow Events | Event_ID must be nonblank and unique |
| PK-05 | RFI Change Links | Link_ID must be nonblank and unique |

## Foreign-key rules

| Rule ID | Relationship | Rule |
|---|---|---|
| FK-01 | RFI Log → Projects | Every RFI Project_ID must exist in Projects |
| FK-02 | Change Orders → Projects | Every change Project_ID must exist in Projects |
| FK-03 | Workflow Events → Projects | Every event Project_ID must exist in Projects |
| FK-04 | RFI Change Links → Projects | Every link Project_ID must exist in Projects |
| FK-05 | RFI Change Links → RFI Log | Every link RFI_ID must exist in RFI Log |
| FK-06 | RFI Change Links → Change Orders | Every link Change_Order_ID must exist in Change Orders |
| FK-07 | Workflow Events → Item table | Item_ID must exist in the table identified by Item_Type |
| FK-08 | Cross-project consistency | RFI, change, event, and link Project_ID values must agree |

## Date-sequence rules

| Rule ID | Rule |
|---|---|
| DT-01 | Planned_Start_Date ≤ Planned_End_Date |
| DT-02 | Actual_Start_Date must be plausible relative to planned dates |
| DT-03 | RFI Submitted_Date ≤ Required_Response_Date |
| DT-04 | RFI Submitted_Date ≤ First_Response_Date ≤ Final_Response_Date when populated |
| DT-05 | RFI Final_Response_Date ≤ Closed_Date when Closed_Date is populated |
| DT-06 | Change Identified_Date ≤ Submitted_Date ≤ Required_Decision_Date |
| DT-07 | Change Submitted_Date ≤ First_Decision_Date when populated |
| DT-08 | Change Submitted_Date ≤ Approved_Date when approved |
| DT-09 | Approved_Date ≤ Forecast_Incorporated_Date when populated |
| DT-10 | Workflow events must be ordered by Item_ID and Event_Sequence |
| DT-11 | Observed workflow-event timestamps must not exceed the cutoff |
| DT-12 | Relationship_Date must be consistent with the related RFI and change dates |

## Numerical rules

| Rule ID | Rule |
|---|---|
| NM-01 | Budgets and contingency must be nonnegative |
| NM-02 | Revision and reopen counts must be nonnegative integers |
| NM-03 | Cost-impact values must follow the documented sign convention |
| NM-04 | Schedule-impact days must be nonnegative unless a deductive convention is explicitly documented |
| NM-05 | Response_Quality_Rating must be between 1 and 5 |
| NM-06 | Approved_Value must be populated for Approved change orders |
| NM-07 | Approved_Value must be zero for Rejected or Withdrawn changes unless an exception is documented |
| NM-08 | Approved schedule days must be consistent with the final disposition |

## Status and completeness rules

| Rule ID | Rule |
|---|---|
| ST-01 | Closed or Answered RFIs require a final response date |
| ST-02 | Closed RFIs require a closed date |
| ST-03 | Approved changes require approved date, approved value, and final pricing status |
| ST-04 | Open or pending records may have blank final dates |
| ST-05 | Forecast incorporation date applies only to approved changes |
| ST-06 | Workflow final status should reconcile with the item master status |

## Controlled-value rules

- Standardize abbreviations, capitalization, whitespace, and synonymous labels.
- Preserve raw values in the raw layer.
- Map unrecognized but valid values to documented controlled categories.
- Use `Unknown` only when a valid value cannot be reconstructed.
- Do not transform a business-valid exception into an error merely because it is uncommon.

## Treatment principles

1. Remove exact duplicates while retaining one canonical record.
2. Reconstruct missing values only from unambiguous evidence.
3. Quarantine invalid parent relationships.
4. Document every repair, removal, standardization, and quarantine.
5. Reconcile raw rows to clean rows and quarantined rows.
6. Test all primary and foreign keys after cleaning.
7. Preserve a repeatable cleaning script or SQL process.
