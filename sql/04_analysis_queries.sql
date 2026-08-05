-- IP-DA-002 Analyze-phase business queries
-- Source: validated clean SQLite database

-- 1. Executive RFI metrics
SELECT
    COUNT(*) AS total_rfi,
    ROUND(AVG(final_response_days),2) AS avg_response_days,
    SUM(CASE WHEN response_compliance_status='On Time' THEN 1 ELSE 0 END) AS on_time_rfi,
    SUM(CASE WHEN response_compliance_status='Overdue Open' THEN 1 ELSE 0 END) AS overdue_open_rfi,
    SUM(CASE WHEN linked_to_change_flag='Yes' THEN 1 ELSE 0 END) AS linked_rfi
FROM vw_rfi_metrics;

-- 2. Executive change metrics
SELECT
    COUNT(*) AS total_changes,
    SUM(CASE WHEN change_status='Approved' THEN 1 ELSE 0 END) AS approved_changes,
    SUM(CASE WHEN change_status='Approved' THEN approved_value ELSE 0 END) AS approved_value,
    SUM(CASE WHEN change_status IN ('Submitted','Under Review','Pending')
             THEN ABS(submitted_value) ELSE 0 END) AS pending_exposure,
    ROUND(AVG(CASE WHEN change_status='Approved' THEN approval_cycle_days END),2) AS avg_approval_days
FROM vw_change_metrics;

-- 3. RFI discipline summary
SELECT
    discipline,
    COUNT(*) AS rfi_count,
    ROUND(AVG(final_response_days),2) AS avg_response_days,
    ROUND(100.0 * SUM(CASE WHEN response_compliance_status='On Time' THEN 1 ELSE 0 END) /
          NULLIF(SUM(CASE WHEN final_response_date IS NOT NULL THEN 1 ELSE 0 END),0),1)
          AS on_time_rate_pct,
    SUM(actual_cost_impact) AS actual_cost_impact,
    SUM(actual_schedule_days) AS actual_schedule_days
FROM vw_rfi_metrics
GROUP BY discipline
ORDER BY avg_response_days DESC;

-- 4. Change-category summary
SELECT
    change_category,
    COUNT(*) AS change_count,
    SUM(CASE WHEN change_status='Approved' THEN approved_value ELSE 0 END) AS approved_value,
    SUM(CASE WHEN change_status IN ('Submitted','Under Review','Pending')
             THEN ABS(submitted_value) ELSE 0 END) AS pending_exposure,
    ROUND(AVG(CASE WHEN change_status='Approved' THEN approval_cycle_days END),2)
          AS avg_approval_days
FROM vw_change_metrics
GROUP BY change_category
ORDER BY approved_value DESC;

-- 5. Workflow bottlenecks
SELECT
    item_type, to_status, assigned_to_role,
    COUNT(*) AS event_count,
    ROUND(AVG(stage_duration_days),2) AS avg_stage_days,
    ROUND(SUM(stage_duration_days),2) AS total_stage_days,
    SUM(CASE WHEN revision_loop_flag='Yes' THEN 1 ELSE 0 END) AS revision_loops
FROM vw_workflow_stage_durations
WHERE stage_duration_days IS NOT NULL
GROUP BY item_type, to_status, assigned_to_role
HAVING COUNT(*) >= 10
ORDER BY total_stage_days DESC;

-- 6. RFI-to-change conversion
SELECT
    COUNT(DISTINCT rfi_id) AS linked_rfi_count,
    COUNT(DISTINCT change_order_id) AS linked_change_count,
    ROUND(AVG(rfi_to_change_identification_days),2) AS avg_identification_lag,
    ROUND(AVG(rfi_to_change_submission_days),2) AS avg_submission_lag
FROM vw_rfi_change_conversion;
