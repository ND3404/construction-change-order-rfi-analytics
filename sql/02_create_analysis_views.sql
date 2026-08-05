CREATE VIEW vw_rfi_metrics AS
SELECT
    r.*,
    CAST(julianday(COALESCE(r.Final_Response_Date, '2025-12-31')) - julianday(r.Submitted_Date) AS INTEGER) AS Response_or_Open_Age_Days,
    CASE WHEN r.Final_Response_Date IS NOT NULL
         THEN CAST(julianday(r.Final_Response_Date) - julianday(r.Submitted_Date) AS INTEGER)
    END AS Final_Response_Days,
    CASE WHEN r.Final_Response_Date IS NOT NULL
         THEN CAST(julianday(r.Final_Response_Date) - julianday(r.Required_Response_Date) AS INTEGER)
         ELSE CAST(julianday('2025-12-31') - julianday(r.Required_Response_Date) AS INTEGER)
    END AS Response_Variance_Days,
    CASE
        WHEN r.Final_Response_Date IS NOT NULL AND date(r.Final_Response_Date) <= date(r.Required_Response_Date) THEN 'On Time'
        WHEN r.Final_Response_Date IS NOT NULL THEN 'Late'
        WHEN date(r.Required_Response_Date) < date('2025-12-31') THEN 'Overdue Open'
        ELSE 'Open Not Due'
    END AS Response_Compliance_Status,
    CASE WHEN EXISTS (SELECT 1 FROM rfi_change_links l WHERE l.RFI_ID = r.RFI_ID) THEN 'Yes' ELSE 'No' END AS Linked_to_Change_Flag
FROM rfi_log r;

CREATE VIEW vw_change_metrics AS
SELECT
    c.*,
    CASE WHEN c.Approved_Date IS NOT NULL
         THEN CAST(julianday(c.Approved_Date) - julianday(c.Submitted_Date) AS INTEGER)
    END AS Approval_Cycle_Days,
    CASE WHEN c.Approved_Date IS NOT NULL
         THEN CAST(julianday(c.Approved_Date) - julianday(c.Required_Decision_Date) AS INTEGER)
         ELSE CAST(julianday('2025-12-31') - julianday(c.Required_Decision_Date) AS INTEGER)
    END AS Decision_Variance_Days,
    CASE WHEN c.Change_Status IN ('Submitted','Under Review','Pending')
         THEN CAST(julianday('2025-12-31') - julianday(c.Submitted_Date) AS INTEGER)
         ELSE 0
    END AS Pending_Age_Days,
    CASE WHEN c.Forecast_Incorporated_Date IS NOT NULL AND c.Approved_Date IS NOT NULL
         THEN CAST(julianday(c.Forecast_Incorporated_Date) - julianday(c.Approved_Date) AS INTEGER)
    END AS Forecast_Incorporation_Lag_Days,
    CASE WHEN EXISTS (SELECT 1 FROM rfi_change_links l WHERE l.Change_Order_ID = c.Change_Order_ID) THEN 'Yes' ELSE 'No' END AS Linked_to_RFI_Flag
FROM change_orders c;

CREATE VIEW vw_workflow_stage_durations AS
WITH ordered AS (
    SELECT
        e.*,
        LAG(e.Event_Timestamp) OVER (PARTITION BY e.Item_Type, e.Item_ID ORDER BY e.Event_Sequence, e.Event_Timestamp) AS Previous_Event_Timestamp,
        LAG(e.Assigned_To_Role) OVER (PARTITION BY e.Item_Type, e.Item_ID ORDER BY e.Event_Sequence, e.Event_Timestamp) AS Previous_Assigned_To_Role
    FROM workflow_events e
)
SELECT
    *,
    ROUND((julianday(Event_Timestamp) - julianday(Previous_Event_Timestamp)) * 24.0, 2) AS Stage_Duration_Hours,
    ROUND(julianday(Event_Timestamp) - julianday(Previous_Event_Timestamp), 2) AS Stage_Duration_Days,
    CASE WHEN Previous_Assigned_To_Role IS NOT NULL AND COALESCE(Assigned_To_Role,'') <> COALESCE(Previous_Assigned_To_Role,'') THEN 'Yes' ELSE 'No' END AS Handoff_Flag,
    CASE WHEN To_Status IN ('Returned for Clarification','Returned for Revision') THEN 'Yes' ELSE 'No' END AS Revision_Loop_Flag
FROM ordered;

CREATE VIEW vw_rfi_change_conversion AS
SELECT
    l.Link_ID,
    l.Project_ID,
    l.RFI_ID,
    l.Change_Order_ID,
    l.Link_Type,
    l.Link_Confidence,
    r.Discipline AS RFI_Discipline,
    r.Priority AS RFI_Priority,
    r.RFI_Type,
    r.Submitted_Date AS RFI_Submitted_Date,
    c.Change_Category,
    c.Originating_Source,
    c.Identified_Date AS Change_Identified_Date,
    c.Submitted_Date AS Change_Submitted_Date,
    c.Approved_Date,
    c.Approved_Value,
    c.Approved_Schedule_Days,
    CAST(julianday(c.Identified_Date) - julianday(r.Submitted_Date) AS INTEGER) AS RFI_to_Change_Identification_Days,
    CAST(julianday(c.Submitted_Date) - julianday(r.Submitted_Date) AS INTEGER) AS RFI_to_Change_Submission_Days
FROM rfi_change_links l
JOIN rfi_log r ON r.RFI_ID = l.RFI_ID
JOIN change_orders c ON c.Change_Order_ID = l.Change_Order_ID;

CREATE VIEW vw_project_workflow_counts AS
SELECT
    p.Project_ID,
    p.Project_Name,
    p.Project_Type,
    p.Delivery_Method,
    p.Original_Budget,
    COUNT(DISTINCT r.RFI_ID) AS RFI_Count,
    COUNT(DISTINCT c.Change_Order_ID) AS Change_Order_Count,
    COUNT(DISTINCT l.Link_ID) AS RFI_Change_Link_Count
FROM projects p
LEFT JOIN rfi_log r ON r.Project_ID = p.Project_ID
LEFT JOIN change_orders c ON c.Project_ID = p.Project_ID
LEFT JOIN rfi_change_links l ON l.Project_ID = p.Project_ID
GROUP BY p.Project_ID;
