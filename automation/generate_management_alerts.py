from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_CUTOFF = date(2025, 12, 31)

PROJECT_RISK = PROJECT_ROOT / "analysis" / "tables" / "project_workflow_risk_summary.csv"
RFI_LOG = PROJECT_ROOT / "data" / "cleaned" / "rfi_log_clean.csv"
CHANGE_LOG = PROJECT_ROOT / "data" / "cleaned" / "change_orders_clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "automation" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    return date.fromisoformat(value) if value else None

alerts: list[dict[str, str | int | float]] = []

# Project-level alerts.
for row in read_csv(PROJECT_RISK):
    score = int(float(row["Workflow_Risk_Score"]))
    if row["Workflow_Health"] == "Red":
        alerts.append({
            "Alert_Type": "Red Project",
            "Severity": "Critical",
            "Project_ID": row["Project_ID"],
            "Item_ID": row["Project_ID"],
            "Project_Name": row["Project_Name"],
            "Condition": f"Workflow risk score {score} (Red)",
            "Current_Value": score,
            "Threshold": 6,
            "Owner_Role": "Project Manager",
            "Required_Action": "Open or update the project recovery plan and assign owners to every Red trigger.",
        })
    pending_pct = float(row["Pending_Exposure_Pct_Budget"])
    if pending_pct > 1.5:
        alerts.append({
            "Alert_Type": "High Pending Exposure",
            "Severity": "Critical",
            "Project_ID": row["Project_ID"],
            "Item_ID": row["Project_ID"],
            "Project_Name": row["Project_Name"],
            "Condition": f"Pending exposure is {pending_pct:.2f}% of project budget",
            "Current_Value": pending_pct,
            "Threshold": 1.5,
            "Owner_Role": "Change Manager",
            "Required_Action": "Review pending items and obtain an approved exposure-reduction plan.",
        })

# RFI alerts.
for row in read_csv(RFI_LOG):
    final_response = parse_date(row.get("Final_Response_Date", ""))
    required = parse_date(row.get("Required_Response_Date", ""))
    submitted = parse_date(row.get("Submitted_Date", ""))
    if final_response is None and required is not None:
        overdue_days = (DATA_CUTOFF - required).days
        priority = row.get("Priority", "")
        if priority in {"High", "Critical"} and overdue_days > 7:
            alerts.append({
                "Alert_Type": "High/Critical Overdue RFI",
                "Severity": "Critical",
                "Project_ID": row["Project_ID"],
                "Item_ID": row["RFI_ID"],
                "Project_Name": "",
                "Condition": f"{priority} RFI overdue by {overdue_days} days",
                "Current_Value": overdue_days,
                "Threshold": 7,
                "Owner_Role": row.get("Responsible_Role", "Design Manager"),
                "Required_Action": "Obtain the response or escalate the required decision immediately.",
            })
        if row.get("Field_Work_Affected") == "Yes" and overdue_days > 0:
            alerts.append({
                "Alert_Type": "Field-Impact Overdue RFI",
                "Severity": "Critical",
                "Project_ID": row["Project_ID"],
                "Item_ID": row["RFI_ID"],
                "Project_Name": "",
                "Condition": f"Open field-impact RFI overdue by {overdue_days} days",
                "Current_Value": overdue_days,
                "Threshold": 0,
                "Owner_Role": "Design Manager",
                "Required_Action": "Protect the field sequence and assign a decision owner and due date.",
            })

# Change-order alerts.
for row in read_csv(CHANGE_LOG):
    submitted = parse_date(row.get("Submitted_Date", ""))
    approved = parse_date(row.get("Approved_Date", ""))
    incorporated = parse_date(row.get("Forecast_Incorporated_Date", ""))
    status = row.get("Change_Status", "")
    if status in {"Submitted", "Under Review", "Pending"} and submitted is not None:
        pending_age = (DATA_CUTOFF - submitted).days
        if pending_age > 35:
            alerts.append({
                "Alert_Type": "Old Pending Change",
                "Severity": "High",
                "Project_ID": row["Project_ID"],
                "Item_ID": row["Change_Order_ID"],
                "Project_Name": "",
                "Condition": f"Pending change age is {pending_age} days",
                "Current_Value": pending_age,
                "Threshold": 35,
                "Owner_Role": "Change Manager",
                "Required_Action": "Decide, negotiate, revise, or document final disposition.",
            })
    if status == "Approved" and approved is not None:
        if incorporated is None:
            alerts.append({
                "Alert_Type": "Approved Not Incorporated",
                "Severity": "High",
                "Project_ID": row["Project_ID"],
                "Item_ID": row["Change_Order_ID"],
                "Project_Name": "",
                "Condition": "Approved change has no observed forecast incorporation date",
                "Current_Value": "",
                "Threshold": "5 business days",
                "Owner_Role": "Project Controls Lead",
                "Required_Action": "Reconcile the change register and update the forecast.",
            })
        else:
            lag = (incorporated - approved).days
            if lag > 5:
                alerts.append({
                    "Alert_Type": "Forecast Incorporation Lag",
                    "Severity": "High",
                    "Project_ID": row["Project_ID"],
                    "Item_ID": row["Change_Order_ID"],
                    "Project_Name": "",
                    "Condition": f"Forecast incorporation lag is {lag} days",
                    "Current_Value": lag,
                    "Threshold": 5,
                    "Owner_Role": "Project Controls Lead",
                    "Required_Action": "Confirm forecast update and document the reconciliation.",
                })

severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
alerts.sort(key=lambda x: (
    severity_order.get(str(x["Severity"]), 9),
    str(x["Project_ID"]),
    str(x["Alert_Type"]),
    str(x["Item_ID"]),
))

output_csv = OUTPUT_DIR / "management_alerts.csv"
headers = [
    "Alert_Type", "Severity", "Project_ID", "Item_ID", "Project_Name",
    "Condition", "Current_Value", "Threshold", "Owner_Role", "Required_Action"
]
with output_csv.open("w", newline="", encoding="utf-8-sig") as handle:
    writer = csv.DictWriter(handle, fieldnames=headers)
    writer.writeheader()
    writer.writerows(alerts)

summary: dict[str, int | str | dict[str, int]] = {
    "Data_Cutoff": DATA_CUTOFF.isoformat(),
    "Alert_Count": len(alerts),
    "By_Severity": {},
    "By_Type": {},
}
for alert in alerts:
    severity = str(alert["Severity"])
    alert_type = str(alert["Alert_Type"])
    summary["By_Severity"][severity] = summary["By_Severity"].get(severity, 0) + 1
    summary["By_Type"][alert_type] = summary["By_Type"].get(alert_type, 0) + 1

(OUTPUT_DIR / "management_alert_summary.json").write_text(
    json.dumps(summary, indent=2), encoding="utf-8"
)

print(json.dumps(summary, indent=2))
