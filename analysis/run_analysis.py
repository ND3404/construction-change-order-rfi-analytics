from __future__ import annotations

import csv
import json
import math
import sqlite3
import statistics
import textwrap
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, pointbiserialr, spearmanr
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline

BASE = Path(__file__).resolve().parents[1]
DB = BASE / "data" / "processed" / "construction_change_order_rfi_analytics.sqlite"
ANALYSIS = BASE / "analysis"
TABLES = ANALYSIS / "tables"
DOC = BASE / "documentation"
SQL_DIR = BASE / "sql"

TABLES.mkdir(parents=True, exist_ok=True)
(ANALYSIS / "excel").mkdir(parents=True, exist_ok=True)
DOC.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

def rows(sql: str, params: tuple = ()) -> list[dict]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]

def row(sql: str, params: tuple = ()) -> dict:
    result = conn.execute(sql, params).fetchone()
    return dict(result) if result else {}

def write_csv(path: Path, records: list[dict], fieldnames: list[str] | None = None) -> None:
    if not records and not fieldnames:
        raise ValueError(f"No records or fieldnames supplied for {path}")
    headers = fieldnames or list(records[0].keys())
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

def median_from_sql(table_expr: str, column: str, where: str = "1=1") -> float | None:
    values = [
        r[0] for r in conn.execute(
            f"SELECT {column} FROM {table_expr} "
            f"WHERE {where} AND {column} IS NOT NULL ORDER BY {column}"
        ).fetchall()
    ]
    return statistics.median(values) if values else None

def pct(numerator: float, denominator: float) -> float:
    return 100.0 * numerator / denominator if denominator else 0.0

def severity(value: float, yellow: float, red: float) -> int:
    return 2 if value > red else 1 if value > yellow else 0

# ---------------------------------------------------------------------------
# Executive KPIs
# ---------------------------------------------------------------------------
rfi = row("""
SELECT
    COUNT(*) AS Total_RFI,
    SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) AS Responded_RFI,
    SUM(CASE WHEN Final_Response_Date IS NULL THEN 1 ELSE 0 END) AS Open_RFI,
    AVG(Final_Response_Days) AS Avg_Response_Days,
    SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) AS On_Time_RFI,
    SUM(CASE WHEN Response_Compliance_Status='Late' THEN 1 ELSE 0 END) AS Late_RFI,
    SUM(CASE WHEN Response_Compliance_Status='Overdue Open' THEN 1 ELSE 0 END) AS Overdue_Open_RFI,
    SUM(CASE WHEN Response_Compliance_Status='Open Not Due' THEN 1 ELSE 0 END) AS Open_Not_Due_RFI,
    SUM(CASE WHEN Linked_to_Change_Flag='Yes' THEN 1 ELSE 0 END) AS Linked_RFI,
    SUM(CASE WHEN Cost_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Cost_Impacted_RFI,
    SUM(CASE WHEN Schedule_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Schedule_Impacted_RFI,
    SUM(Actual_Cost_Impact) AS Actual_RFI_Cost_Impact,
    SUM(Actual_Schedule_Days) AS Actual_RFI_Schedule_Days,
    AVG(Response_Quality_Rating) AS Avg_Response_Quality
FROM vw_rfi_metrics
""")

change = row("""
SELECT
    COUNT(*) AS Total_Changes,
    SUM(CASE WHEN Change_Status='Approved' THEN 1 ELSE 0 END) AS Approved_Changes,
    SUM(CASE WHEN Change_Status='Rejected' THEN 1 ELSE 0 END) AS Rejected_Changes,
    SUM(CASE WHEN Change_Status='Withdrawn' THEN 1 ELSE 0 END) AS Withdrawn_Changes,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN 1 ELSE 0 END) AS Pending_Changes,
    SUM(CASE WHEN Change_Status='Approved' THEN Approved_Value ELSE 0 END) AS Approved_Value,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END) AS Pending_Exposure,
    AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END) AS Avg_Approval_Days,
    AVG(CASE WHEN Change_Status='Approved' THEN Forecast_Incorporation_Lag_Days END) AS Avg_Forecast_Lag,
    SUM(CASE WHEN Linked_to_RFI_Flag='Yes' THEN 1 ELSE 0 END) AS Linked_Changes,
    SUM(CASE WHEN Change_Status='Approved' THEN Approved_Schedule_Days ELSE 0 END) AS Approved_Schedule_Days,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') AND Pending_Age_Days>35 THEN 1 ELSE 0 END) AS Old_Pending_Count,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') AND Pending_Age_Days>35 THEN ABS(Submitted_Value) ELSE 0 END) AS Old_Pending_Exposure,
    SUM(CASE WHEN Change_Status='Approved' AND Forecast_Incorporated_Date IS NULL THEN 1 ELSE 0 END) AS Approved_Not_Incorporated
FROM vw_change_metrics
""")

conversion = row("""
SELECT
    COUNT(*) AS Link_Count,
    COUNT(DISTINCT RFI_ID) AS Linked_RFI_Count,
    COUNT(DISTINCT Change_Order_ID) AS Linked_Change_Count,
    AVG(RFI_to_Change_Identification_Days) AS Avg_Identification_Lag_Days,
    AVG(RFI_to_Change_Submission_Days) AS Avg_Submission_Lag_Days
FROM vw_rfi_change_conversion
""")

linked_unique = row("""
SELECT
    COUNT(*) AS Linked_Change_Count,
    SUM(Approved_Value) AS Linked_Approved_Value,
    SUM(Approved_Schedule_Days) AS Linked_Approved_Schedule_Days
FROM vw_change_metrics
WHERE Linked_to_RFI_Flag='Yes'
""")

project_count = row("SELECT COUNT(*) AS Project_Count FROM projects")["Project_Count"]

executive_kpis = [
    {"KPI": "Projects", "Value": project_count, "Unit": "count"},
    {"KPI": "RFIs", "Value": rfi["Total_RFI"], "Unit": "count"},
    {"KPI": "Average RFI response", "Value": round(rfi["Avg_Response_Days"], 2), "Unit": "days"},
    {"KPI": "Median RFI response", "Value": median_from_sql("vw_rfi_metrics", "Final_Response_Days"), "Unit": "days"},
    {"KPI": "RFI on-time rate", "Value": round(pct(rfi["On_Time_RFI"], rfi["Responded_RFI"]), 2), "Unit": "percent"},
    {"KPI": "Open RFIs", "Value": rfi["Open_RFI"], "Unit": "count"},
    {"KPI": "Overdue open RFIs", "Value": rfi["Overdue_Open_RFI"], "Unit": "count"},
    {"KPI": "RFI-to-change conversion", "Value": round(pct(rfi["Linked_RFI"], rfi["Total_RFI"]), 2), "Unit": "percent"},
    {"KPI": "RFI actual cost impact", "Value": rfi["Actual_RFI_Cost_Impact"], "Unit": "USD"},
    {"KPI": "RFI actual schedule impact", "Value": rfi["Actual_RFI_Schedule_Days"], "Unit": "days"},
    {"KPI": "Change orders", "Value": change["Total_Changes"], "Unit": "count"},
    {"KPI": "Approved changes", "Value": change["Approved_Changes"], "Unit": "count"},
    {"KPI": "Approved change value", "Value": change["Approved_Value"], "Unit": "USD"},
    {"KPI": "Pending change exposure", "Value": change["Pending_Exposure"], "Unit": "USD absolute"},
    {"KPI": "Average approval cycle", "Value": round(change["Avg_Approval_Days"], 2), "Unit": "days"},
    {"KPI": "Median approval cycle", "Value": median_from_sql("vw_change_metrics", "Approval_Cycle_Days", "Change_Status='Approved'"), "Unit": "days"},
    {"KPI": "Old pending changes >35 days", "Value": change["Old_Pending_Count"], "Unit": "count"},
    {"KPI": "Average forecast incorporation lag", "Value": round(change["Avg_Forecast_Lag"], 2), "Unit": "days"},
    {"KPI": "Linked approved change value", "Value": linked_unique["Linked_Approved_Value"], "Unit": "USD unique changes"},
    {"KPI": "Median RFI-to-change identification lag", "Value": median_from_sql("vw_rfi_change_conversion", "RFI_to_Change_Identification_Days"), "Unit": "days"},
]
write_csv(TABLES / "executive_kpis.csv", executive_kpis)

# ---------------------------------------------------------------------------
# Breakdown tables
# ---------------------------------------------------------------------------
rfi_discipline = rows("""
SELECT
    Discipline,
    COUNT(*) AS RFI_Count,
    SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) AS Responded_Count,
    ROUND(AVG(Final_Response_Days),2) AS Avg_Response_Days,
    ROUND(100.0 * SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END),0),1) AS On_Time_Rate_Pct,
    SUM(CASE WHEN Response_Compliance_Status='Overdue Open' THEN 1 ELSE 0 END) AS Overdue_Open_Count,
    ROUND(100.0 * SUM(CASE WHEN Linked_to_Change_Flag='Yes' THEN 1 ELSE 0 END) / COUNT(*),1) AS RFI_to_Change_Rate_Pct,
    SUM(CASE WHEN Cost_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Cost_Impacted_Count,
    SUM(CASE WHEN Schedule_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Schedule_Impacted_Count,
    ROUND(SUM(Actual_Cost_Impact),0) AS Actual_Cost_Impact,
    SUM(Actual_Schedule_Days) AS Actual_Schedule_Days
FROM vw_rfi_metrics
GROUP BY Discipline
ORDER BY Avg_Response_Days DESC
""")
write_csv(TABLES / "rfi_discipline_summary.csv", rfi_discipline)

rfi_type = rows("""
SELECT
    RFI_Type,
    COUNT(*) AS RFI_Count,
    ROUND(AVG(Final_Response_Days),2) AS Avg_Response_Days,
    ROUND(100.0 * SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END),0),1) AS On_Time_Rate_Pct,
    SUM(CASE WHEN Response_Compliance_Status='Overdue Open' THEN 1 ELSE 0 END) AS Overdue_Open_Count,
    ROUND(100.0 * SUM(CASE WHEN Linked_to_Change_Flag='Yes' THEN 1 ELSE 0 END) / COUNT(*),1) AS RFI_to_Change_Rate_Pct,
    SUM(CASE WHEN Cost_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Cost_Impacted_Count,
    SUM(CASE WHEN Schedule_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Schedule_Impacted_Count,
    ROUND(SUM(Actual_Cost_Impact),0) AS Actual_Cost_Impact,
    SUM(Actual_Schedule_Days) AS Actual_Schedule_Days
FROM vw_rfi_metrics
GROUP BY RFI_Type
ORDER BY Actual_Cost_Impact DESC
""")
write_csv(TABLES / "rfi_type_summary.csv", rfi_type)

change_category = rows("""
SELECT
    Change_Category,
    COUNT(*) AS Change_Count,
    SUM(CASE WHEN Change_Status='Approved' THEN 1 ELSE 0 END) AS Approved_Count,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN 1 ELSE 0 END) AS Pending_Count,
    ROUND(SUM(CASE WHEN Change_Status='Approved' THEN Approved_Value ELSE 0 END),0) AS Approved_Value,
    ROUND(SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END),0) AS Pending_Exposure,
    ROUND(AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END),2) AS Avg_Approval_Days,
    SUM(CASE WHEN Change_Status='Approved' THEN Approved_Schedule_Days ELSE 0 END) AS Approved_Schedule_Days,
    SUM(CASE WHEN Linked_to_RFI_Flag='Yes' THEN 1 ELSE 0 END) AS Linked_Change_Count,
    ROUND(AVG(CASE WHEN Change_Status='Approved' THEN Forecast_Incorporation_Lag_Days END),2) AS Avg_Forecast_Lag_Days
FROM vw_change_metrics
GROUP BY Change_Category
ORDER BY Approved_Value DESC
""")
write_csv(TABLES / "change_category_summary.csv", change_category)

change_party = rows("""
SELECT
    Initiating_Party,
    COUNT(*) AS Change_Count,
    SUM(CASE WHEN Change_Status='Approved' THEN 1 ELSE 0 END) AS Approved_Count,
    SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN 1 ELSE 0 END) AS Pending_Count,
    ROUND(SUM(CASE WHEN Change_Status='Approved' THEN Approved_Value ELSE 0 END),0) AS Approved_Value,
    ROUND(SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END),0) AS Pending_Exposure,
    ROUND(AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END),2) AS Avg_Approval_Days,
    SUM(CASE WHEN Change_Status='Approved' THEN Approved_Schedule_Days ELSE 0 END) AS Approved_Schedule_Days
FROM vw_change_metrics
GROUP BY Initiating_Party
ORDER BY Approved_Value DESC
""")
write_csv(TABLES / "change_initiating_party_summary.csv", change_party)

workflow = rows("""
SELECT
    Item_Type,
    To_Status,
    Assigned_To_Role,
    COUNT(*) AS Event_Count,
    ROUND(AVG(Stage_Duration_Days),2) AS Avg_Stage_Days,
    ROUND(SUM(Stage_Duration_Days),2) AS Total_Stage_Days,
    SUM(CASE WHEN Handoff_Flag='Yes' THEN 1 ELSE 0 END) AS Handoff_Count,
    SUM(CASE WHEN Revision_Loop_Flag='Yes' THEN 1 ELSE 0 END) AS Revision_Loop_Count
FROM vw_workflow_stage_durations
WHERE Stage_Duration_Days IS NOT NULL
GROUP BY Item_Type, To_Status, Assigned_To_Role
HAVING COUNT(*) >= 10
ORDER BY Total_Stage_Days DESC
""")
write_csv(TABLES / "workflow_bottleneck_summary.csv", workflow)

yearly = rows("""
WITH years AS (
    SELECT CAST(strftime('%Y', Submitted_Date) AS INTEGER) AS Year,
           COUNT(*) AS RFI_Count,
           AVG(Final_Response_Days) AS Avg_RFI_Response_Days,
           SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) AS Responded,
           SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) AS On_Time
    FROM vw_rfi_metrics GROUP BY 1
),
changes AS (
    SELECT CAST(strftime('%Y', Submitted_Date) AS INTEGER) AS Year,
           COUNT(*) AS Change_Count,
           SUM(CASE WHEN Change_Status='Approved' THEN Approved_Value ELSE 0 END) AS Approved_Value,
           AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END) AS Avg_Approval_Cycle_Days,
           SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END) AS Pending_Exposure
    FROM vw_change_metrics GROUP BY 1
)
SELECT y.Year, y.RFI_Count, ROUND(y.Avg_RFI_Response_Days,2) AS Avg_RFI_Response_Days,
       ROUND(100.0*y.On_Time/NULLIF(y.Responded,0),1) AS On_Time_Rate_Pct,
       c.Change_Count, ROUND(c.Approved_Value,0) AS Approved_Value,
       ROUND(c.Avg_Approval_Cycle_Days,2) AS Avg_Approval_Cycle_Days,
       ROUND(c.Pending_Exposure,0) AS Pending_Exposure
FROM years y LEFT JOIN changes c USING(Year)
ORDER BY y.Year
""")
write_csv(TABLES / "yearly_trend_summary.csv", yearly)

owner_segment = rows("""
WITH rfi AS (
    SELECT p.Owner_Decision_Profile AS Segment, r.*
    FROM projects p JOIN vw_rfi_metrics r ON r.Project_ID=p.Project_ID
),
change_data AS (
    SELECT p.Owner_Decision_Profile AS Segment, c.*
    FROM projects p JOIN vw_change_metrics c ON c.Project_ID=p.Project_ID
)
SELECT s.Segment,
       (SELECT COUNT(*) FROM rfi WHERE Segment=s.Segment) AS RFI_Count,
       ROUND((SELECT AVG(Final_Response_Days) FROM rfi WHERE Segment=s.Segment),2) AS Avg_RFI_Response_Days,
       ROUND(100.0*(SELECT SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) FROM rfi WHERE Segment=s.Segment) /
           NULLIF((SELECT SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) FROM rfi WHERE Segment=s.Segment),0),1) AS On_Time_Rate_Pct,
       (SELECT COUNT(*) FROM change_data WHERE Segment=s.Segment) AS Change_Count,
       ROUND((SELECT AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END) FROM change_data WHERE Segment=s.Segment),2) AS Avg_Approval_Cycle_Days,
       ROUND((SELECT SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END) FROM change_data WHERE Segment=s.Segment),0) AS Pending_Exposure
FROM (SELECT DISTINCT Owner_Decision_Profile AS Segment FROM projects) s
ORDER BY CASE s.Segment WHEN 'Fast' THEN 1 WHEN 'Standard' THEN 2 ELSE 3 END
""")
for record in owner_segment:
    record["Segment_Type"] = "Owner Decision Profile"

digital_segment = rows("""
WITH rfi AS (
    SELECT p.Digital_Coordination_Level AS Segment, r.*
    FROM projects p JOIN vw_rfi_metrics r ON r.Project_ID=p.Project_ID
),
change_data AS (
    SELECT p.Digital_Coordination_Level AS Segment, c.*
    FROM projects p JOIN vw_change_metrics c ON c.Project_ID=p.Project_ID
)
SELECT s.Segment,
       (SELECT COUNT(*) FROM rfi WHERE Segment=s.Segment) AS RFI_Count,
       ROUND((SELECT AVG(Final_Response_Days) FROM rfi WHERE Segment=s.Segment),2) AS Avg_RFI_Response_Days,
       ROUND(100.0*(SELECT SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) FROM rfi WHERE Segment=s.Segment) /
           NULLIF((SELECT SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) FROM rfi WHERE Segment=s.Segment),0),1) AS On_Time_Rate_Pct,
       (SELECT COUNT(*) FROM change_data WHERE Segment=s.Segment) AS Change_Count,
       ROUND((SELECT AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END) FROM change_data WHERE Segment=s.Segment),2) AS Avg_Approval_Cycle_Days,
       ROUND((SELECT SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END) FROM change_data WHERE Segment=s.Segment),0) AS Pending_Exposure
FROM (SELECT DISTINCT Digital_Coordination_Level AS Segment FROM projects) s
ORDER BY CASE s.Segment WHEN 'High' THEN 1 WHEN 'Moderate' THEN 2 ELSE 3 END
""")
for record in digital_segment:
    record["Segment_Type"] = "Digital Coordination Level"

segment_records = owner_segment + digital_segment
write_csv(
    TABLES / "lifecycle_segment_summary.csv",
    segment_records,
    ["Segment_Type", "Segment", "RFI_Count", "Avg_RFI_Response_Days",
     "On_Time_Rate_Pct", "Change_Count", "Avg_Approval_Cycle_Days", "Pending_Exposure"]
)

# ---------------------------------------------------------------------------
# Project-level risk summary
# ---------------------------------------------------------------------------
project_base = rows("""
WITH rfi AS (
    SELECT Project_ID,
           COUNT(*) AS RFI_Count,
           SUM(CASE WHEN Final_Response_Date IS NOT NULL THEN 1 ELSE 0 END) AS Responded_Count,
           AVG(Final_Response_Days) AS Avg_Response_Days,
           SUM(CASE WHEN Response_Compliance_Status='On Time' THEN 1 ELSE 0 END) AS On_Time_Count,
           SUM(CASE WHEN Response_Compliance_Status='Overdue Open' THEN 1 ELSE 0 END) AS Overdue_Open_Count,
           SUM(CASE WHEN Priority IN ('High','Critical') AND Response_Compliance_Status='Overdue Open' THEN 1 ELSE 0 END) AS High_Critical_Overdue_Count,
           SUM(CASE WHEN Cost_Impact_Flag='Yes' THEN 1 ELSE 0 END) AS Cost_Impacted_RFI_Count,
           SUM(Actual_Cost_Impact) AS Actual_RFI_Cost_Impact,
           SUM(Actual_Schedule_Days) AS Actual_RFI_Schedule_Days,
           SUM(CASE WHEN Linked_to_Change_Flag='Yes' THEN 1 ELSE 0 END) AS Linked_RFI_Count
    FROM vw_rfi_metrics GROUP BY Project_ID
),
changes AS (
    SELECT Project_ID,
           COUNT(*) AS Change_Count,
           SUM(CASE WHEN Change_Status='Approved' THEN 1 ELSE 0 END) AS Approved_Change_Count,
           SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN 1 ELSE 0 END) AS Pending_Change_Count,
           SUM(CASE WHEN Change_Status='Approved' THEN Approved_Value ELSE 0 END) AS Approved_Change_Value,
           SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') THEN ABS(Submitted_Value) ELSE 0 END) AS Pending_Change_Exposure,
           AVG(CASE WHEN Change_Status='Approved' THEN Approval_Cycle_Days END) AS Avg_Approval_Cycle_Days,
           SUM(CASE WHEN Change_Status IN ('Submitted','Under Review','Pending') AND Pending_Age_Days>35 THEN 1 ELSE 0 END) AS Old_Pending_Count,
           AVG(CASE WHEN Change_Status='Approved' THEN Forecast_Incorporation_Lag_Days END) AS Avg_Forecast_Lag_Days,
           SUM(CASE WHEN Change_Status='Approved' AND Forecast_Incorporated_Date IS NULL THEN 1 ELSE 0 END) AS Approved_Not_Incorporated_Count,
           SUM(CASE WHEN Linked_to_RFI_Flag='Yes' THEN 1 ELSE 0 END) AS Linked_Change_Count
    FROM vw_change_metrics GROUP BY Project_ID
),
workflow AS (
    SELECT Project_ID,
           COUNT(*) AS Event_Count,
           SUM(CASE WHEN Handoff_Flag='Yes' THEN 1 ELSE 0 END) AS Handoff_Count,
           SUM(CASE WHEN Revision_Loop_Flag='Yes' THEN 1 ELSE 0 END) AS Revision_Loop_Count,
           AVG(Stage_Duration_Days) AS Avg_Stage_Duration_Days
    FROM vw_workflow_stage_durations GROUP BY Project_ID
)
SELECT p.Project_ID, p.Project_Name, p.Project_Type, p.Delivery_Method,
       p.Complexity_Level, p.Digital_Coordination_Level, p.Owner_Decision_Profile,
       p.Original_Budget,
       COALESCE(rfi.RFI_Count,0) AS RFI_Count,
       COALESCE(rfi.Responded_Count,0) AS Responded_Count,
       COALESCE(rfi.Avg_Response_Days,0) AS Avg_Response_Days,
       COALESCE(rfi.On_Time_Count,0) AS On_Time_Count,
       COALESCE(rfi.Overdue_Open_Count,0) AS Overdue_Open_Count,
       COALESCE(rfi.High_Critical_Overdue_Count,0) AS High_Critical_Overdue_Count,
       COALESCE(rfi.Cost_Impacted_RFI_Count,0) AS Cost_Impacted_RFI_Count,
       COALESCE(rfi.Actual_RFI_Cost_Impact,0) AS Actual_RFI_Cost_Impact,
       COALESCE(rfi.Actual_RFI_Schedule_Days,0) AS Actual_RFI_Schedule_Days,
       COALESCE(rfi.Linked_RFI_Count,0) AS Linked_RFI_Count,
       COALESCE(changes.Change_Count,0) AS Change_Count,
       COALESCE(changes.Approved_Change_Count,0) AS Approved_Change_Count,
       COALESCE(changes.Pending_Change_Count,0) AS Pending_Change_Count,
       COALESCE(changes.Approved_Change_Value,0) AS Approved_Change_Value,
       COALESCE(changes.Pending_Change_Exposure,0) AS Pending_Change_Exposure,
       COALESCE(changes.Avg_Approval_Cycle_Days,0) AS Avg_Approval_Cycle_Days,
       COALESCE(changes.Old_Pending_Count,0) AS Old_Pending_Count,
       COALESCE(changes.Avg_Forecast_Lag_Days,0) AS Avg_Forecast_Lag_Days,
       COALESCE(changes.Approved_Not_Incorporated_Count,0) AS Approved_Not_Incorporated_Count,
       COALESCE(changes.Linked_Change_Count,0) AS Linked_Change_Count,
       COALESCE(workflow.Event_Count,0) AS Event_Count,
       COALESCE(workflow.Handoff_Count,0) AS Handoff_Count,
       COALESCE(workflow.Revision_Loop_Count,0) AS Revision_Loop_Count,
       COALESCE(workflow.Avg_Stage_Duration_Days,0) AS Avg_Stage_Duration_Days
FROM projects p
LEFT JOIN rfi ON rfi.Project_ID=p.Project_ID
LEFT JOIN changes ON changes.Project_ID=p.Project_ID
LEFT JOIN workflow ON workflow.Project_ID=p.Project_ID
ORDER BY p.Project_ID
""")

project_summary: list[dict] = []
for p in project_base:
    on_time_rate = pct(p["On_Time_Count"], p["Responded_Count"])
    overdue_rate = pct(p["Overdue_Open_Count"], p["RFI_Count"])
    high_critical_rate = pct(p["High_Critical_Overdue_Count"], p["RFI_Count"])
    conversion_rate = pct(p["Linked_RFI_Count"], p["RFI_Count"])
    pending_exposure_pct = pct(p["Pending_Change_Exposure"], p["Original_Budget"])
    approved_change_pct = pct(p["Approved_Change_Value"], p["Original_Budget"])
    not_incorporated_rate = pct(p["Approved_Not_Incorporated_Count"], p["Approved_Change_Count"])

    components = {
        "Response_Points": severity(p["Avg_Response_Days"], 10, 15),
        "Overdue_Points": severity(overdue_rate, 15, 30),
        "High_Critical_Overdue_Points": severity(high_critical_rate, 2, 5),
        "Approval_Points": severity(p["Avg_Approval_Cycle_Days"], 20, 35),
        "Pending_Exposure_Points": severity(pending_exposure_pct, 0.5, 1.5),
        "Forecast_Lag_Points": severity(p["Avg_Forecast_Lag_Days"], 5, 10),
        "Not_Incorporated_Points": severity(not_incorporated_rate, 5, 15),
    }
    risk_score = sum(components.values())
    health = "Red" if risk_score >= 6 else "Yellow" if risk_score >= 3 else "Green"

    record = {
        **p,
        "On_Time_Rate_Pct": round(on_time_rate, 2),
        "Overdue_Open_Rate_Pct": round(overdue_rate, 2),
        "High_Critical_Overdue_Rate_Pct": round(high_critical_rate, 2),
        "RFI_to_Change_Rate_Pct": round(conversion_rate, 2),
        "Pending_Exposure_Pct_Budget": round(pending_exposure_pct, 3),
        "Approved_Change_Pct_Budget": round(approved_change_pct, 3),
        "Approved_Not_Incorporated_Rate_Pct": round(not_incorporated_rate, 2),
        **components,
        "Workflow_Risk_Score": risk_score,
        "Red_Indicator_Count": sum(v == 2 for v in components.values()),
        "Yellow_Indicator_Count": sum(v == 1 for v in components.values()),
        "Workflow_Health": health,
    }
    project_summary.append(record)

project_summary.sort(
    key=lambda x: (
        x["Workflow_Risk_Score"],
        x["Pending_Exposure_Pct_Budget"],
        x["Overdue_Open_Rate_Pct"],
        x["Avg_Response_Days"],
    ),
    reverse=True,
)
write_csv(TABLES / "project_workflow_risk_summary.csv", project_summary)

top_10 = project_summary[:10]
write_csv(TABLES / "top_10_priority_projects.csv", top_10)

health_counts = Counter(p["Workflow_Health"] for p in project_summary)
health_table = [
    {"Workflow_Health": level, "Project_Count": health_counts.get(level, 0)}
    for level in ["Red", "Yellow", "Green"]
]
write_csv(TABLES / "project_health_distribution.csv", health_table)

# ---------------------------------------------------------------------------
# Statistical associations
# ---------------------------------------------------------------------------
rfi_stats = rows("""
SELECT Final_Response_Days, Revision_Count, Reopen_Count, Cost_Impact_Flag,
       Schedule_Impact_Flag, Linked_to_Change_Flag, Response_Quality_Rating
FROM vw_rfi_metrics
WHERE Final_Response_Days IS NOT NULL
""")
response_days = np.array([float(r["Final_Response_Days"]) for r in rfi_stats])
rfi_revisions = np.array([float(r["Revision_Count"]) for r in rfi_stats])
rfi_reopens = np.array([float(r["Reopen_Count"]) for r in rfi_stats])
quality = np.array([float(r["Response_Quality_Rating"]) for r in rfi_stats])
cost_flag = np.array([1 if r["Cost_Impact_Flag"] == "Yes" else 0 for r in rfi_stats])
schedule_flag = np.array([1 if r["Schedule_Impact_Flag"] == "Yes" else 0 for r in rfi_stats])
linked_flag = np.array([1 if r["Linked_to_Change_Flag"] == "Yes" else 0 for r in rfi_stats])

change_stats = rows("""
SELECT Approval_Cycle_Days, Revision_Count, Linked_to_RFI_Flag,
       ABS(Submitted_Value) AS Abs_Submitted_Value, Approved_Schedule_Days
FROM vw_change_metrics
WHERE Change_Status='Approved' AND Approval_Cycle_Days IS NOT NULL
""")
approval_days = np.array([float(r["Approval_Cycle_Days"]) for r in change_stats])
change_revisions = np.array([float(r["Revision_Count"]) for r in change_stats])
change_linked = np.array([1 if r["Linked_to_RFI_Flag"] == "Yes" else 0 for r in change_stats])
change_value = np.array([float(r["Abs_Submitted_Value"] or 0) for r in change_stats])

project_response = np.array([float(p["Avg_Response_Days"]) for p in project_summary])
project_approval = np.array([float(p["Avg_Approval_Cycle_Days"]) for p in project_summary])

def association_record(
    relationship: str,
    method: str,
    statistic: float,
    p_value: float,
    n: int,
    interpretation: str,
) -> dict:
    return {
        "Relationship": relationship,
        "Method": method,
        "Statistic": round(float(statistic), 4),
        "P_Value": float(p_value),
        "N": n,
        "Interpretation": interpretation,
    }

associations: list[dict] = []
for label, binary, interpretation in [
    ("RFI response days vs cost-impact flag", cost_flag, "Longer response time shows a moderate positive association with cost impact."),
    ("RFI response days vs schedule-impact flag", schedule_flag, "Longer response time shows a modest positive association with schedule impact."),
    ("RFI response days vs linked-to-change flag", linked_flag, "Response time alone has only a weak association with later change linkage."),
]:
    result = pointbiserialr(binary, response_days)
    associations.append(association_record(label, "Point-biserial r", result.statistic, result.pvalue, len(response_days), interpretation))

for label, x, y, interpretation in [
    ("RFI revision count vs response days", rfi_revisions, response_days, "More revision activity is moderately associated with longer response cycles."),
    ("RFI reopen count vs response days", rfi_reopens, response_days, "Reopened RFIs are associated with longer response cycles."),
    ("RFI response quality vs response days", quality, response_days, "Longer response cycles are associated with lower response-quality ratings in the synthetic data."),
    ("Change revision count vs approval days", change_revisions, approval_days, "More change revisions are moderately associated with longer approval cycles."),
    ("Change submitted value vs approval days", change_value, approval_days, "Change size has little association with approval cycle in this portfolio."),
]:
    result = spearmanr(x, y)
    associations.append(association_record(label, "Spearman rho", result.statistic, result.pvalue, len(x), interpretation))

change_link_result = pointbiserialr(change_linked, approval_days)
associations.append(association_record(
    "Change linked-to-RFI flag vs approval days",
    "Point-biserial r",
    change_link_result.statistic,
    change_link_result.pvalue,
    len(approval_days),
    "Linked and unlinked changes have essentially the same approval-cycle distribution."
))

project_pearson = pearsonr(project_response, project_approval)
associations.append(association_record(
    "Project average RFI response vs average change approval cycle",
    "Pearson r",
    project_pearson.statistic,
    project_pearson.pvalue,
    len(project_response),
    "Projects with slower RFI response also tend to have slower change approval; this is the strongest tested portfolio-level relationship."
))
project_spearman = spearmanr(project_response, project_approval)
associations.append(association_record(
    "Project average RFI response vs average change approval cycle",
    "Spearman rho",
    project_spearman.statistic,
    project_spearman.pvalue,
    len(project_response),
    "The strong monotonic relationship is consistent with the Pearson result."
))
write_csv(TABLES / "association_results.csv", associations)

# ---------------------------------------------------------------------------
# Exploratory RFI-to-change logistic models
# ---------------------------------------------------------------------------
early_rows = rows("""
SELECT r.Linked_to_Change_Flag, r.Discipline, r.Priority, r.RFI_Type,
       r.Submitted_By_Role, r.Responsible_Role, r.Drawing_Reference_Count,
       p.Project_Type, p.Delivery_Method, p.Complexity_Level,
       p.Digital_Coordination_Level, p.Owner_Decision_Profile
FROM vw_rfi_metrics r
JOIN projects p ON p.Project_ID=r.Project_ID
""")
X_early = [{k: v for k, v in r.items() if k != "Linked_to_Change_Flag"} for r in early_rows]
y_early = [1 if r["Linked_to_Change_Flag"] == "Yes" else 0 for r in early_rows]

diagnostic_rows = rows("""
SELECT r.Linked_to_Change_Flag, r.Discipline, r.Priority, r.RFI_Type,
       r.Revision_Count, r.Reopen_Count, r.Cost_Impact_Flag, r.Schedule_Impact_Flag,
       r.Field_Work_Affected, r.Drawing_Reference_Count, r.Response_Quality_Rating,
       r.Final_Response_Days,
       p.Project_Type, p.Delivery_Method, p.Complexity_Level,
       p.Digital_Coordination_Level, p.Owner_Decision_Profile
FROM vw_rfi_metrics r
JOIN projects p ON p.Project_ID=r.Project_ID
""")
X_diagnostic = []
y_diagnostic = []
for r in diagnostic_rows:
    features = {k: v for k, v in r.items() if k != "Linked_to_Change_Flag"}
    features["Open_Flag"] = "Yes" if features["Final_Response_Days"] is None else "No"
    features["Final_Response_Days"] = float(features["Final_Response_Days"] or 0)
    X_diagnostic.append(features)
    y_diagnostic.append(1 if r["Linked_to_Change_Flag"] == "Yes" else 0)

def model_auc(X: list[dict], y: list[int]) -> tuple[float, float, list[float]]:
    pipeline = Pipeline([
        ("vectorizer", DictVectorizer(sparse=True)),
        ("model", LogisticRegression(max_iter=1000, class_weight="balanced", solver="liblinear")),
    ])
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    values = cross_val_score(pipeline, X, y, cv=cv, scoring="roc_auc")
    return float(values.mean()), float(values.std()), [float(v) for v in values]

early_mean, early_std, early_folds = model_auc(X_early, y_early)
diagnostic_mean, diagnostic_std, diagnostic_folds = model_auc(X_diagnostic, y_diagnostic)

model_results = [
    {
        "Model": "Submission-only exploratory logistic model",
        "Available_Information": "Priority, RFI type, discipline, roles, drawing count, project attributes",
        "Mean_CV_AUC": round(early_mean, 4),
        "Std_CV_AUC": round(early_std, 4),
        "Fold_AUCs": "; ".join(f"{v:.4f}" for v in early_folds),
        "Interpretation": "Performance is near chance; submission attributes alone do not identify later change linkage in this synthetic portfolio.",
        "Production_Use": "No",
    },
    {
        "Model": "Diagnostic exploratory logistic model",
        "Available_Information": "Submission attributes plus response, revision, quality, and impact indicators",
        "Mean_CV_AUC": round(diagnostic_mean, 4),
        "Std_CV_AUC": round(diagnostic_std, 4),
        "Fold_AUCs": "; ".join(f"{v:.4f}" for v in diagnostic_folds),
        "Interpretation": "Post-submission workflow and impact indicators improve discrimination, but performance remains moderate.",
        "Production_Use": "No",
    },
]
write_csv(TABLES / "exploratory_model_results.csv", model_results)

analysis_summary = {
    "project_code": "IP-DA-002",
    "phase": "Analyze",
    "status": "Complete",
    "projects": project_count,
    "rfi": {
        **rfi,
        "Median_Response_Days": median_from_sql("vw_rfi_metrics", "Final_Response_Days"),
        "On_Time_Rate_Pct": pct(rfi["On_Time_RFI"], rfi["Responded_RFI"]),
        "RFI_to_Change_Rate_Pct": pct(rfi["Linked_RFI"], rfi["Total_RFI"]),
    },
    "change_orders": {
        **change,
        "Median_Approval_Days": median_from_sql("vw_change_metrics", "Approval_Cycle_Days", "Change_Status='Approved'"),
        "Median_Forecast_Lag_Days": median_from_sql("vw_change_metrics", "Forecast_Incorporation_Lag_Days", "Change_Status='Approved'"),
    },
    "conversion": {
        **conversion,
        **linked_unique,
        "Median_Identification_Lag_Days": median_from_sql("vw_rfi_change_conversion", "RFI_to_Change_Identification_Days"),
        "Median_Submission_Lag_Days": median_from_sql("vw_rfi_change_conversion", "RFI_to_Change_Submission_Days"),
    },
    "project_health": dict(health_counts),
    "strongest_tested_relationship": {
        "relationship": "Project average RFI response vs average change approval cycle",
        "pearson_r": float(project_pearson.statistic),
        "r_squared": float(project_pearson.statistic ** 2),
        "p_value": float(project_pearson.pvalue),
    },
    "exploratory_models": model_results,
}
(DOC / "analyze_validation_summary.json").write_text(json.dumps(analysis_summary, indent=2), encoding="utf-8")

print(json.dumps({
    "status": "Analyze tables refreshed",
    "analysis_tables": len(list(TABLES.glob("*.csv"))),
    "project_health": dict(health_counts),
    "strongest_relationship_r": round(float(project_pearson.statistic), 4),
    "early_model_auc": round(early_mean, 4),
    "diagnostic_model_auc": round(diagnostic_mean, 4),
}, indent=2))
