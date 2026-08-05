
from __future__ import annotations

import csv
import json
import math
import random
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20260803
rng = random.Random(SEED)

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
DOC_DIR = ROOT / "documentation"
RAW_DIR.mkdir(parents=True, exist_ok=True)
DOC_DIR.mkdir(parents=True, exist_ok=True)

CUTOFF = date(2025, 12, 31)

PROJECT_TYPES = [
    "Residential", "Commercial", "Institutional", "Industrial",
    "Heavy Civil & Infrastructure", "Mixed-Use"
]
STATES = {
    "UT": ["Salt Lake City", "Lehi", "Provo", "Ogden", "St. George"],
    "CO": ["Denver", "Aurora", "Colorado Springs", "Fort Collins"],
    "AZ": ["Phoenix", "Mesa", "Scottsdale", "Tucson"],
    "NV": ["Las Vegas", "Henderson", "Reno"],
    "TX": ["Austin", "Dallas", "Fort Worth", "San Antonio", "Houston"],
    "CA": ["Sacramento", "San Diego", "Fresno", "Riverside"],
    "WA": ["Seattle", "Tacoma", "Spokane", "Bellevue"],
    "OR": ["Portland", "Salem", "Eugene"],
    "ID": ["Boise", "Meridian", "Idaho Falls"],
    "NM": ["Albuquerque", "Santa Fe", "Las Cruces"],
}
REGIONS = {
    "UT": "Mountain", "CO": "Mountain", "AZ": "Southwest", "NV": "West",
    "TX": "South", "CA": "West", "WA": "Pacific Northwest", "OR": "Pacific Northwest",
    "ID": "Mountain", "NM": "Southwest",
}
CLIENT_TYPES = ["Private Developer", "Public Agency", "Institutional Owner", "Corporate Owner", "Nonprofit"]
CONTRACT_TYPES = ["Lump Sum", "Guaranteed Maximum Price", "Cost Plus", "Unit Price", "Design-Build Agreement"]
DELIVERY_METHODS = ["Design-Bid-Build", "Design-Build", "CMAR", "IPD"]
COMPLEXITIES = ["Low", "Moderate", "High", "Very High"]
DIGITAL_LEVELS = ["Low", "Moderate", "High"]
PHASES = ["Design", "Procurement", "Construction", "Commissioning", "Closeout"]
PROJECT_STATUS = ["Active", "Substantially Complete", "Completed", "On Hold"]

DISCIPLINES = [
    "Architectural", "Structural", "Mechanical", "Electrical", "Plumbing",
    "Civil", "Fire Protection", "Controls", "General", "Specialty Systems"
]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
RFI_TYPES = [
    "Design Clarification", "Coordination Conflict", "Missing Information",
    "Constructability", "Substitution Request", "Field Condition", "Code Compliance"
]
ROLES = [
    "General Contractor", "Subcontractor", "Architect", "Engineer",
    "Owner Representative", "Construction Manager", "Cost Manager",
    "Design Manager", "Project Manager"
]
RFI_STATUSES = [
    "Open", "In Review", "Awaiting Designer", "Awaiting Owner",
    "Returned for Clarification", "Answered", "Closed"
]
CHANGE_CATEGORIES = [
    "Owner-Directed Change", "Design Error or Omission", "Unforeseen Condition",
    "Code or Regulatory Requirement", "Value Engineering", "Scope Clarification",
    "Substitution", "Schedule Acceleration", "Quantity Variation"
]
INITIATING_PARTIES = [
    "Owner", "Architect", "Engineer", "General Contractor", "Subcontractor",
    "Authority Having Jurisdiction", "Construction Manager"
]
CHANGE_TYPES = ["Additive", "Deductive", "Zero-Cost", "Time Only"]
ORIGIN_SOURCES = ["RFI", "Owner Request", "Field Condition", "Design Revision", "Submittal Review", "Schedule Recovery"]
CHANGE_STATUSES = ["Draft", "Submitted", "Under Review", "Pending", "Approved", "Rejected", "Withdrawn"]
PRICING_STATUSES = ["ROM", "Pricing in Progress", "Submitted", "Negotiating", "Final"]
AUTH_TYPES = ["None", "Field Directive", "Construction Change Directive", "Owner Authorization", "Executed Change Order"]
COST_CODE_GROUPS = ["General Conditions", "Sitework", "Concrete", "Metals", "Envelope", "Interiors", "MEP", "Equipment", "Specialties"]

PROJECT_PREFIXES = [
    "Canyon", "Summit", "Northstar", "Red Rock", "Blue Mesa", "Silver Creek",
    "Mountain Gate", "Copper Ridge", "Pioneer", "Desert View", "Riverbend",
    "Aspen", "Granite", "Sunset", "Evergreen", "Liberty", "Frontier", "Vista"
]
PROJECT_NOUNS = {
    "Residential": ["Residences", "Housing Community", "Apartments", "Neighborhood"],
    "Commercial": ["Corporate Center", "Retail Pavilion", "Office Campus", "Marketplace"],
    "Institutional": ["Medical Pavilion", "Community College", "Research Center", "Civic Complex"],
    "Industrial": ["Manufacturing Facility", "Distribution Center", "Processing Plant", "Logistics Hub"],
    "Heavy Civil & Infrastructure": ["Bridge Rehabilitation", "Transit Center", "Water Facility", "Roadway Program"],
    "Mixed-Use": ["Transit-Oriented Development", "Urban Village", "Mixed-Use District", "Town Center"],
}

def iso(d):
    return d.isoformat() if isinstance(d, date) else ""

def dt_iso(d, hour=8, minute=0):
    if isinstance(d, date) and not isinstance(d, datetime):
        d = datetime(d.year, d.month, d.day, hour, minute)
    return d.isoformat(timespec="minutes") if isinstance(d, datetime) else ""

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def weighted_choice(options, weights):
    return rng.choices(options, weights=weights, k=1)[0]

def random_date(start, end):
    if end <= start:
        return start
    return start + timedelta(days=rng.randint(0, (end - start).days))

def add_days(d, days):
    return d + timedelta(days=int(days))

def money_round(v):
    if abs(v) < 10000:
        return round(v / 100) * 100
    return round(v / 1000) * 1000

def allocate_counts(weights, total, minimum=0):
    counts = [minimum for _ in weights]
    remaining = total - minimum * len(weights)
    if remaining < 0:
        raise ValueError("Total is smaller than minimum allocation.")
    indexes = list(range(len(weights)))
    for idx in rng.choices(indexes, weights=weights, k=remaining):
        counts[idx] += 1
    return counts

def write_csv(path, rows, headers):
    with Path(path).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
projects = []
project_profiles = {}
used_names = set()

type_budget_ranges = {
    "Residential": (12_000_000, 180_000_000),
    "Commercial": (15_000_000, 220_000_000),
    "Institutional": (25_000_000, 300_000_000),
    "Industrial": (30_000_000, 350_000_000),
    "Heavy Civil & Infrastructure": (35_000_000, 420_000_000),
    "Mixed-Use": (45_000_000, 450_000_000),
}
complexity_factor = {"Low": 0.75, "Moderate": 1.0, "High": 1.25, "Very High": 1.55}
digital_factor = {"Low": 1.18, "Moderate": 1.0, "High": 0.86}
decision_factor = {"Fast": 0.78, "Standard": 1.0, "Slow": 1.28}

for i in range(1, 91):
    project_id = f"PRJ-{i:03d}"
    project_type = weighted_choice(PROJECT_TYPES, [18, 18, 14, 14, 14, 12])
    state = weighted_choice(list(STATES), [14, 10, 10, 8, 16, 10, 8, 7, 8, 9])
    city = rng.choice(STATES[state])
    complexity = weighted_choice(COMPLEXITIES, [18, 40, 30, 12])
    digital = weighted_choice(DIGITAL_LEVELS, [22, 48, 30])
    owner_decision = weighted_choice(["Fast", "Standard", "Slow"], [22, 53, 25])
    delivery = weighted_choice(DELIVERY_METHODS, [31, 28, 32, 9])
    contract = {
        "Design-Bid-Build": weighted_choice(CONTRACT_TYPES, [42, 20, 8, 24, 6]),
        "Design-Build": weighted_choice(CONTRACT_TYPES, [20, 28, 18, 8, 26]),
        "CMAR": weighted_choice(CONTRACT_TYPES, [12, 58, 20, 5, 5]),
        "IPD": weighted_choice(CONTRACT_TYPES, [8, 28, 52, 4, 8]),
    }[delivery]
    client = weighted_choice(CLIENT_TYPES, [36, 22, 20, 16, 6])
    lo, hi = type_budget_ranges[project_type]
    budget = money_round(math.exp(rng.uniform(math.log(lo), math.log(hi))))
    contingency_rate = rng.uniform(0.035, 0.09) * complexity_factor[complexity]
    contingency = money_round(budget * clamp(contingency_rate, 0.035, 0.12))
    start = date(2021, 1, 1) + timedelta(days=rng.randint(0, 1250))
    duration_months = int(clamp(rng.gauss(24 + 9 * (complexity_factor[complexity] - 1), 7), 12, 52))
    planned_end = start + timedelta(days=int(duration_months * 30.44))
    actual_start = start + timedelta(days=max(-14, int(rng.gauss(8, 14))))
    schedule_pressure = (
        0.12 * complexity_factor[complexity]
        + 0.08 * digital_factor[digital]
        + 0.10 * decision_factor[owner_decision]
        + rng.gauss(0, 0.08)
    )
    forecast_delay = int(clamp((schedule_pressure - 0.25) * 110, -20, 140))
    forecast_end = planned_end + timedelta(days=forecast_delay)
    elapsed = (CUTOFF - actual_start).days / max(1, (forecast_end - actual_start).days)
    if elapsed >= 1.08:
        status = "Completed"
        phase = "Closeout"
    elif elapsed >= 0.94:
        status = "Substantially Complete"
        phase = weighted_choice(["Commissioning", "Closeout"], [65, 35])
    elif rng.random() < 0.035:
        status = "On Hold"
        phase = weighted_choice(["Design", "Procurement", "Construction"], [25, 25, 50])
    else:
        status = "Active"
        if elapsed < 0.18:
            phase = "Design"
        elif elapsed < 0.32:
            phase = "Procurement"
        elif elapsed < 0.84:
            phase = "Construction"
        else:
            phase = "Commissioning"

    prefix = rng.choice(PROJECT_PREFIXES)
    noun = rng.choice(PROJECT_NOUNS[project_type])
    name = f"{prefix} {noun}"
    suffix = 2
    while name in used_names:
        name = f"{prefix} {noun} {suffix}"
        suffix += 1
    used_names.add(name)

    project = {
        "Project_ID": project_id,
        "Project_Name": name,
        "Project_Type": project_type,
        "City": city,
        "State": state,
        "Region": REGIONS[state],
        "Client_Type": client,
        "Contract_Type": contract,
        "Delivery_Method": delivery,
        "Complexity_Level": complexity,
        "Digital_Coordination_Level": digital,
        "Owner_Decision_Profile": owner_decision,
        "Original_Budget": budget,
        "Original_Contingency": contingency,
        "Planned_Start_Date": iso(start),
        "Planned_End_Date": iso(planned_end),
        "Actual_Start_Date": iso(actual_start),
        "Forecast_End_Date": iso(forecast_end),
        "Project_Status": status,
        "Current_Phase": phase,
        "Project_Manager_ID": f"PM-{rng.randint(1, 24):03d}",
        "Design_Manager_ID": f"DM-{rng.randint(1, 16):03d}",
        "Change_Manager_ID": f"CM-{rng.randint(1, 12):03d}",
    }
    projects.append(project)
    project_profiles[project_id] = {
        "complexity": complexity_factor[complexity],
        "digital": digital_factor[digital],
        "decision": decision_factor[owner_decision],
        "budget": budget,
        "start": actual_start,
        "end": min(max(actual_start + timedelta(days=30), forecast_end), CUTOFF),
        "phase": phase,
        "type": project_type,
        "delivery": delivery,
        "contract": contract,
    }

# ---------------------------------------------------------------------------
# Allocate RFI and CO volumes
# ---------------------------------------------------------------------------
rfi_weights = []
co_weights = []
for project in projects:
    p = project_profiles[project["Project_ID"]]
    scale = max(0.45, math.log10(p["budget"] / 1_000_000 + 1))
    rfi_weights.append(scale * p["complexity"] * p["digital"] * rng.uniform(0.75, 1.25))
    co_weights.append(scale * p["complexity"] * p["decision"] * rng.uniform(0.70, 1.30))

rfi_counts = allocate_counts(rfi_weights, 3320, minimum=12)
co_counts = allocate_counts(co_weights, 1120, minimum=4)

# ---------------------------------------------------------------------------
# RFIs
# ---------------------------------------------------------------------------
rfis = []
rfi_by_project = defaultdict(list)
rfi_counter = 1

discipline_delay = {
    "Architectural": 1.0, "Structural": 1.20, "Mechanical": 1.25,
    "Electrical": 1.30, "Plumbing": 1.05, "Civil": 1.10,
    "Fire Protection": 1.12, "Controls": 1.32, "General": 0.90,
    "Specialty Systems": 1.18,
}
priority_required = {"Low": 14, "Medium": 10, "High": 5, "Critical": 3}
priority_response_factor = {"Low": 1.12, "Medium": 1.0, "High": 0.90, "Critical": 0.82}
priority_impact_factor = {"Low": 0.55, "Medium": 1.0, "High": 1.55, "Critical": 2.2}
type_impact_factor = {
    "Design Clarification": 0.75, "Coordination Conflict": 1.35,
    "Missing Information": 1.12, "Constructability": 1.25,
    "Substitution Request": 0.90, "Field Condition": 1.55,
    "Code Compliance": 1.40,
}

for project, count in zip(projects, rfi_counts):
    pid = project["Project_ID"]
    profile = project_profiles[pid]
    start = max(profile["start"], date(2022, 1, 1))
    end = min(profile["end"], CUTOFF)
    if end <= start:
        end = start + timedelta(days=60)
    for local_no in range(1, count + 1):
        rfi_id = f"RFI-{rfi_counter:05d}"
        rfi_counter += 1
        discipline = weighted_choice(DISCIPLINES, [15, 13, 15, 15, 9, 8, 6, 5, 7, 7])
        priority = weighted_choice(PRIORITIES, [18, 54, 23, 5])
        rfi_type = weighted_choice(RFI_TYPES, [27, 22, 14, 12, 8, 12, 5])
        submitted = random_date(start, end)
        required_days = priority_required[priority] + rng.randint(-1, 2)
        required = submitted + timedelta(days=max(1, required_days))
        base_days = (
            7.2
            * discipline_delay[discipline]
            * profile["complexity"]
            * profile["decision"]
            * profile["digital"]
            * priority_response_factor[priority]
        )
        response_days = max(1, int(rng.lognormvariate(math.log(max(2, base_days)), 0.42)))
        revision_count = 0
        if rng.random() < 0.18 * profile["complexity"]:
            revision_count = 1
        if rng.random() < 0.035 * profile["complexity"]:
            revision_count += 1
        reopen_count = 1 if rng.random() < 0.055 * profile["complexity"] else 0
        response_days += revision_count * rng.randint(3, 8) + reopen_count * rng.randint(4, 11)

        first_response = submitted + timedelta(days=max(1, response_days - revision_count * rng.randint(1, 4)))
        final_response = submitted + timedelta(days=response_days)
        recent_open_probability = 0.08 + (0.16 if (CUTOFF - submitted).days < 50 else 0)
        is_open = rng.random() < recent_open_probability or final_response > CUTOFF
        if is_open:
            status = weighted_choice(
                ["Open", "In Review", "Awaiting Designer", "Awaiting Owner", "Returned for Clarification"],
                [15, 27, 25, 20, 13],
            )
            first_response_value = "" if rng.random() < 0.62 or first_response > CUTOFF else iso(first_response)
            final_response_value = ""
            closed_value = ""
        else:
            status = weighted_choice(["Answered", "Closed"], [26, 74])
            first_response_value = iso(first_response)
            final_response_value = iso(final_response)
            closed_value = iso(final_response + timedelta(days=rng.randint(0, 4))) if status == "Closed" else ""

        impact_score = (
            0.08
            + 0.018 * max(0, response_days - required_days)
            + 0.11 * (profile["complexity"] - 1)
            + 0.10 * (type_impact_factor[rfi_type] - 1)
            + 0.08 * (priority_impact_factor[priority] - 1)
            + 0.08 * revision_count
        )
        impact_probability = clamp(impact_score, 0.03, 0.72)
        cost_impact = rng.random() < impact_probability
        schedule_impact = rng.random() < clamp(impact_probability * 0.78, 0.02, 0.55)
        estimated_cost = 0
        actual_cost = 0
        if cost_impact:
            magnitude = rng.lognormvariate(math.log(18_000 * priority_impact_factor[priority]), 1.0)
            estimated_cost = money_round(clamp(magnitude, 1_000, profile["budget"] * 0.018))
            actual_cost = money_round(estimated_cost * rng.uniform(0.70, 1.45))
        estimated_days = 0
        actual_days = 0
        if schedule_impact:
            estimated_days = int(clamp(rng.lognormvariate(math.log(3.2 * priority_impact_factor[priority]), 0.7), 1, 45))
            actual_days = int(clamp(estimated_days * rng.uniform(0.65, 1.55), 1, 60))

        quality = int(clamp(round(5.2 - 0.09 * max(0, response_days - required_days) - 0.7 * revision_count + rng.gauss(0, 0.7)), 1, 5))
        submitted_by = weighted_choice(["General Contractor", "Subcontractor", "Construction Manager"], [42, 43, 15])
        responsible_role = {
            "Architectural": "Architect", "Structural": "Engineer", "Mechanical": "Engineer",
            "Electrical": "Engineer", "Plumbing": "Engineer", "Civil": "Engineer",
            "Fire Protection": "Engineer", "Controls": "Engineer", "General": "Construction Manager",
            "Specialty Systems": "Design Manager",
        }[discipline]
        if rng.random() < 0.13:
            responsible_role = "Owner Representative"

        title = f"{discipline} {rfi_type} - Area {rng.choice(['A','B','C','D','E'])}{rng.randint(1, 12)}"
        rfi = {
            "RFI_ID": rfi_id,
            "Project_ID": pid,
            "RFI_Number": f"RFI-{local_no:04d}",
            "RFI_Title": title,
            "Discipline": discipline,
            "Priority": priority,
            "RFI_Type": rfi_type,
            "Submitted_Date": iso(submitted),
            "Required_Response_Date": iso(required),
            "First_Response_Date": first_response_value,
            "Final_Response_Date": final_response_value,
            "Closed_Date": closed_value,
            "RFI_Status": status,
            "Submitted_By_Role": submitted_by,
            "Responsible_Role": responsible_role,
            "Revision_Count": revision_count,
            "Reopen_Count": reopen_count,
            "Cost_Impact_Flag": "Yes" if cost_impact else "No",
            "Estimated_Cost_Impact": estimated_cost,
            "Actual_Cost_Impact": actual_cost,
            "Schedule_Impact_Flag": "Yes" if schedule_impact else "No",
            "Estimated_Schedule_Days": estimated_days,
            "Actual_Schedule_Days": actual_days,
            "Field_Work_Affected": "Yes" if (cost_impact or schedule_impact) and rng.random() < 0.62 else "No",
            "Drawing_Reference_Count": rng.randint(0, 6),
            "Response_Quality_Rating": quality,
        }
        rfis.append(rfi)
        rfi_by_project[pid].append(rfi)

# ---------------------------------------------------------------------------
# Change orders
# ---------------------------------------------------------------------------
change_orders = []
co_by_project = defaultdict(list)
co_counter = 1

category_cycle = {
    "Owner-Directed Change": 1.25,
    "Design Error or Omission": 1.18,
    "Unforeseen Condition": 1.05,
    "Code or Regulatory Requirement": 1.12,
    "Value Engineering": 0.88,
    "Scope Clarification": 0.95,
    "Substitution": 0.86,
    "Schedule Acceleration": 1.22,
    "Quantity Variation": 0.90,
}
category_value = {
    "Owner-Directed Change": 1.45,
    "Design Error or Omission": 1.15,
    "Unforeseen Condition": 1.28,
    "Code or Regulatory Requirement": 1.0,
    "Value Engineering": 0.75,
    "Scope Clarification": 0.70,
    "Substitution": 0.62,
    "Schedule Acceleration": 1.32,
    "Quantity Variation": 0.82,
}

for project, count in zip(projects, co_counts):
    pid = project["Project_ID"]
    profile = project_profiles[pid]
    start = max(profile["start"], date(2022, 1, 1))
    end = min(profile["end"], CUTOFF)
    if end <= start:
        end = start + timedelta(days=90)
    for local_no in range(1, count + 1):
        co_id = f"CO-{co_counter:05d}"
        co_counter += 1
        category = weighted_choice(CHANGE_CATEGORIES, [20, 17, 14, 7, 8, 10, 8, 6, 10])
        initiating = {
            "Owner-Directed Change": weighted_choice(INITIATING_PARTIES, [75, 5, 4, 5, 2, 1, 8]),
            "Design Error or Omission": weighted_choice(INITIATING_PARTIES, [5, 35, 32, 7, 3, 1, 17]),
            "Unforeseen Condition": weighted_choice(INITIATING_PARTIES, [8, 4, 8, 35, 25, 2, 18]),
        }.get(category, weighted_choice(INITIATING_PARTIES, [18, 15, 15, 20, 14, 5, 13]))
        discipline = weighted_choice(DISCIPLINES, [13, 11, 14, 14, 9, 9, 6, 5, 8, 11])
        change_type = weighted_choice(CHANGE_TYPES, [74, 12, 8, 6])
        origin = {
            "Owner-Directed Change": "Owner Request",
            "Design Error or Omission": weighted_choice(["RFI", "Design Revision", "Submittal Review"], [50, 35, 15]),
            "Unforeseen Condition": weighted_choice(["Field Condition", "RFI"], [72, 28]),
        }.get(category, weighted_choice(ORIGIN_SOURCES, [24, 16, 18, 16, 12, 14]))

        latest_identified = max(start, end - timedelta(days=35))
        identified = random_date(start, latest_identified)
        pre_submit_days = int(clamp(rng.lognormvariate(math.log(5.5 * profile["complexity"]), 0.55), 1, 50))
        submitted = min(CUTOFF, identified + timedelta(days=pre_submit_days))
        required = submitted + timedelta(days=20)
        revision_count = 0
        if rng.random() < 0.32 * profile["complexity"]:
            revision_count = 1
        if rng.random() < 0.08 * profile["complexity"]:
            revision_count += 1
        if rng.random() < 0.018 * profile["complexity"]:
            revision_count += 1

        cycle = int(clamp(
            rng.lognormvariate(
                math.log(18 * category_cycle[category] * profile["decision"] * profile["complexity"]),
                0.45,
            ) + revision_count * rng.randint(5, 12),
            4,
            145,
        ))
        first_decision = submitted + timedelta(days=max(2, int(cycle * rng.uniform(0.35, 0.72))))
        decision_date = submitted + timedelta(days=cycle)
        recency = (CUTOFF - submitted).days
        if decision_date > CUTOFF:
            status = weighted_choice(["Submitted", "Under Review", "Pending"], [12, 38, 50])
        elif recency < max(25, cycle) and rng.random() < 0.70:
            status = weighted_choice(["Submitted", "Under Review", "Pending"], [18, 42, 40])
        else:
            status = weighted_choice(["Approved", "Rejected", "Withdrawn", "Pending"], [64, 10, 7, 19])

        value_base = profile["budget"] * rng.lognormvariate(math.log(0.0023 * category_value[category]), 0.9)
        submitted_value = money_round(clamp(value_base, 5_000, profile["budget"] * 0.055))
        if change_type == "Deductive":
            submitted_value *= -1
        elif change_type in ("Zero-Cost", "Time Only"):
            submitted_value = 0

        negotiated_value = ""
        approved_value = ""
        approved_date = ""
        closed_date = ""
        pricing_status = "Submitted"
        authorization = "None"
        if status == "Approved":
            negotiated_value = money_round(submitted_value * rng.uniform(0.76, 1.04))
            approved_value = money_round(negotiated_value * rng.uniform(0.96, 1.02))
            approved_date = iso(decision_date)
            closed_date = iso(decision_date + timedelta(days=rng.randint(1, 10)))
            pricing_status = "Final"
            authorization = weighted_choice(AUTH_TYPES[1:], [10, 12, 36, 42])
        elif status == "Rejected":
            negotiated_value = money_round(submitted_value * rng.uniform(0.4, 0.85))
            approved_value = 0
            closed_date = iso(decision_date + timedelta(days=rng.randint(0, 5)))
            pricing_status = "Final"
        elif status == "Withdrawn":
            negotiated_value = ""
            approved_value = 0
            closed_date = iso(decision_date)
            pricing_status = weighted_choice(["ROM", "Pricing in Progress", "Submitted"], [25, 35, 40])
        else:
            pricing_status = weighted_choice(["ROM", "Pricing in Progress", "Submitted", "Negotiating"], [12, 28, 30, 30])
            if status == "Pending" and rng.random() < 0.45:
                negotiated_value = money_round(submitted_value * rng.uniform(0.78, 1.08))

        requested_days = 0
        approved_days = 0
        time_probability = clamp(0.16 + 0.12 * (category_value[category] - 0.7) + 0.08 * profile["complexity"], 0.10, 0.62)
        if change_type == "Time Only" or rng.random() < time_probability:
            requested_days = int(clamp(rng.lognormvariate(math.log(6 * category_value[category]), 0.8), 1, 65))
            if status == "Approved":
                approved_days = int(clamp(requested_days * rng.uniform(0.55, 1.05), 0, 70))

        forecast_date = ""
        if status == "Approved":
            lag = int(clamp(rng.lognormvariate(math.log(5.5 * profile["decision"]), 0.62), 0, 40))
            if rng.random() < 0.92:
                incorporated = decision_date + timedelta(days=lag)
                forecast_date = iso(incorporated) if incorporated <= CUTOFF else ""

        co = {
            "Change_Order_ID": co_id,
            "Project_ID": pid,
            "Change_Number": f"CO-{local_no:03d}",
            "Change_Title": f"{category} - {discipline} Area {rng.choice(['A','B','C','D'])}{rng.randint(1,10)}",
            "Change_Category": category,
            "Initiating_Party": initiating,
            "Discipline": discipline,
            "Change_Type": change_type,
            "Originating_Source": origin,
            "Identified_Date": iso(identified),
            "Submitted_Date": iso(submitted),
            "Required_Decision_Date": iso(required),
            "First_Decision_Date": iso(first_decision) if status not in ("Submitted", "Draft") else "",
            "Approved_Date": approved_date,
            "Closed_Date": closed_date,
            "Change_Status": status,
            "Submitted_Value": submitted_value,
            "Negotiated_Value": negotiated_value,
            "Approved_Value": approved_value,
            "Requested_Schedule_Days": requested_days,
            "Approved_Schedule_Days": approved_days,
            "Revision_Count": revision_count,
            "Pricing_Status": pricing_status,
            "Authorization_Type": authorization,
            "Forecast_Incorporated_Date": forecast_date,
            "Cost_Code_Group": weighted_choice(COST_CODE_GROUPS, [12, 10, 11, 8, 11, 14, 23, 5, 6]),
        }
        change_orders.append(co)
        co_by_project[pid].append(co)

# ---------------------------------------------------------------------------
# RFI-to-change links
# ---------------------------------------------------------------------------
links = []
link_counter = 1
link_target = 680

link_candidates = []
for pid, cos in co_by_project.items():
    project_rfis = rfi_by_project[pid]
    if not project_rfis:
        continue
    for co in cos:
        origin_bonus = 3.0 if co["Originating_Source"] == "RFI" else 1.0
        cat_bonus = 1.6 if co["Change_Category"] in ("Design Error or Omission", "Unforeseen Condition", "Scope Clarification") else 1.0
        if rng.random() < clamp(0.28 * origin_bonus * cat_bonus, 0.16, 0.88):
            co_date = date.fromisoformat(co["Identified_Date"])
            eligible = []
            for rfi in project_rfis:
                rfi_date = date.fromisoformat(rfi["Submitted_Date"])
                delta = (co_date - rfi_date).days
                if -10 <= delta <= 180:
                    score = 1.0
                    if rfi["Cost_Impact_Flag"] == "Yes": score *= 2.2
                    if rfi["Schedule_Impact_Flag"] == "Yes": score *= 1.7
                    if rfi["Discipline"] == co["Discipline"]: score *= 1.8
                    if rfi["RFI_Type"] in ("Coordination Conflict", "Field Condition", "Missing Information"): score *= 1.5
                    score *= max(0.35, 1.4 - abs(delta - 25) / 160)
                    eligible.append((rfi, score))
            if eligible:
                selected = rng.choices([x[0] for x in eligible], weights=[x[1] for x in eligible], k=1)[0]
                link_candidates.append((selected, co))

# Ensure exactly the target by adding/removing plausible pairs.
unique_pairs = {}
for rfi, co in link_candidates:
    unique_pairs[(rfi["RFI_ID"], co["Change_Order_ID"])] = (rfi, co)
link_candidates = list(unique_pairs.values())

all_possible = []
for pid, cos in co_by_project.items():
    project_rfis = rfi_by_project[pid]
    if not project_rfis:
        continue
    impacted = [r for r in project_rfis if r["Cost_Impact_Flag"] == "Yes" or r["Schedule_Impact_Flag"] == "Yes"]
    pool = impacted or project_rfis
    for co in cos:
        if co["Originating_Source"] in ("RFI", "Field Condition", "Design Revision"):
            for rfi in rng.sample(pool, min(3, len(pool))):
                key = (rfi["RFI_ID"], co["Change_Order_ID"])
                if key not in unique_pairs:
                    all_possible.append((rfi, co))
                    unique_pairs[key] = (rfi, co)

rng.shuffle(all_possible)
while len(link_candidates) < link_target and all_possible:
    link_candidates.append(all_possible.pop())
if len(link_candidates) > link_target:
    rng.shuffle(link_candidates)
    link_candidates = link_candidates[:link_target]

for rfi, co in link_candidates:
    rfi_date = date.fromisoformat(rfi["Submitted_Date"])
    co_date = date.fromisoformat(co["Identified_Date"])
    rel_date = max(rfi_date, co_date)
    same_discipline = rfi["Discipline"] == co["Discipline"]
    link_type = weighted_choice(
        ["Direct Cause", "Supporting Documentation", "Related Scope", "Potential Relationship"],
        [44 if co["Originating_Source"] == "RFI" else 25, 28, 22, 6],
    )
    confidence = "High" if link_type == "Direct Cause" and same_discipline else weighted_choice(["High", "Medium", "Low"], [28, 58, 14])
    links.append({
        "Link_ID": f"LNK-{link_counter:05d}",
        "Project_ID": co["Project_ID"],
        "RFI_ID": rfi["RFI_ID"],
        "Change_Order_ID": co["Change_Order_ID"],
        "Link_Type": link_type,
        "Link_Confidence": confidence,
        "Relationship_Date": iso(rel_date),
        "Relationship_Notes_Category": weighted_choice(
            ["Design clarification led to scope change", "Field condition documented by RFI",
             "Pricing support", "Schedule support", "Related coordination issue"],
            [28, 24, 20, 12, 16],
        ),
    })
    link_counter += 1

# ---------------------------------------------------------------------------
# Workflow events
# ---------------------------------------------------------------------------
events = []
event_counter = 1

def append_event(project_id, item_type, item_id, seq, when, from_status, to_status,
                 action_by, assigned_to, action, revision, decision, comment):
    global event_counter
    events.append({
        "Event_ID": f"EVT-{event_counter:06d}",
        "Project_ID": project_id,
        "Item_Type": item_type,
        "Item_ID": item_id,
        "Event_Sequence": seq,
        "Event_Timestamp": dt_iso(when),
        "From_Status": from_status,
        "To_Status": to_status,
        "Action_By_Role": action_by,
        "Assigned_To_Role": assigned_to,
        "Event_Action": action,
        "Revision_Number": revision,
        "Decision_Required_Flag": decision,
        "Comment_Category": comment,
    })
    event_counter += 1

for rfi in rfis:
    pid = rfi["Project_ID"]
    submitted = date.fromisoformat(rfi["Submitted_Date"])
    seq = 1
    append_event(
        pid, "RFI", rfi["RFI_ID"], seq,
        datetime.combine(submitted, datetime.min.time()) + timedelta(hours=8),
        "", "Submitted", rfi["Submitted_By_Role"], rfi["Responsible_Role"],
        "Submit", 0, "Yes", "Initial submission"
    )
    seq += 1

    # Add a revision-loop event only when the RFI was returned.
    if rfi["Revision_Count"] > 0:
        anchor = (
            date.fromisoformat(rfi["First_Response_Date"])
            if rfi["First_Response_Date"]
            else submitted + timedelta(days=rng.randint(5, 15))
        )
        returned = min(CUTOFF, max(submitted + timedelta(days=1), anchor - timedelta(days=rng.randint(2, 5))))
        append_event(
            pid, "RFI", rfi["RFI_ID"], seq,
            datetime.combine(returned, datetime.min.time()) + timedelta(hours=13),
            "Submitted", "Returned for Clarification",
            rfi["Responsible_Role"], rfi["Submitted_By_Role"],
            "Return", 1, "Yes", "Insufficient information"
        )
        seq += 1

    if rfi["Final_Response_Date"]:
        final = date.fromisoformat(rfi["Final_Response_Date"])
        final_status = "Closed" if rfi["RFI_Status"] == "Closed" else "Answered"
        append_event(
            pid, "RFI", rfi["RFI_ID"], seq,
            datetime.combine(final, datetime.min.time()) + timedelta(hours=15),
            "Returned for Clarification" if rfi["Revision_Count"] > 0 else "Submitted",
            final_status, rfi["Responsible_Role"], rfi["Submitted_By_Role"],
            "Respond and close" if final_status == "Closed" else "Respond",
            rfi["Revision_Count"], "No", "Final response"
        )
    else:
        current = rfi["RFI_Status"]
        current_date = min(CUTOFF, submitted + timedelta(days=rng.randint(2, 14)))
        append_event(
            pid, "RFI", rfi["RFI_ID"], seq,
            datetime.combine(current_date, datetime.min.time()) + timedelta(hours=11),
            "Submitted", current, "Design Manager", rfi["Responsible_Role"],
            "Assign or escalate", rfi["Revision_Count"], "Yes", "Current open status"
        )

for co in change_orders:
    pid = co["Project_ID"]
    identified = date.fromisoformat(co["Identified_Date"])
    submitted = date.fromisoformat(co["Submitted_Date"])
    seq = 1
    append_event(
        pid, "Change Order", co["Change_Order_ID"], seq,
        datetime.combine(identified, datetime.min.time()) + timedelta(hours=9),
        "", "Identified", "Project Manager", "Cost Manager",
        "Identify", 0, "Yes", "Potential change identified"
    )
    seq += 1
    append_event(
        pid, "Change Order", co["Change_Order_ID"], seq,
        datetime.combine(submitted, datetime.min.time()) + timedelta(hours=10),
        "Identified", "Submitted", "Cost Manager", "Owner Representative",
        "Submit pricing", 0, "Yes", "Commercial submission"
    )
    seq += 1

    # Add one representative revision-loop event when revisions occurred.
    if int(co["Revision_Count"]) > 0:
        if co["Approved_Date"]:
            decision_anchor = date.fromisoformat(co["Approved_Date"])
            revision_date = submitted + timedelta(days=max(2, int((decision_anchor - submitted).days * 0.55)))
        else:
            revision_date = submitted + timedelta(days=rng.randint(7, 20))
        append_event(
            pid, "Change Order", co["Change_Order_ID"], seq,
            datetime.combine(revision_date, datetime.min.time()) + timedelta(hours=14),
            "Submitted", "Returned for Revision",
            "Owner Representative", "Cost Manager",
            "Return pricing", 1, "Yes", "Pricing clarification"
        )
        seq += 1

    if co["Change_Status"] == "Approved":
        final_date = date.fromisoformat(co["Approved_Date"])
        final_status = "Approved"
        action = "Approve"
    elif co["Change_Status"] in ("Rejected", "Withdrawn"):
        final_date = date.fromisoformat(co["Closed_Date"])
        final_status = co["Change_Status"]
        action = co["Change_Status"]
    else:
        final_date = min(CUTOFF, submitted + timedelta(days=rng.randint(7, 28)))
        final_status = co["Change_Status"]
        action = "Hold or review"

    append_event(
        pid, "Change Order", co["Change_Order_ID"], seq,
        datetime.combine(final_date, datetime.min.time()) + timedelta(hours=15),
        "Returned for Revision" if int(co["Revision_Count"]) > 0 else "Submitted",
        final_status, "Owner Representative", "Project Manager",
        action, co["Revision_Count"],
        "No" if final_status in ("Approved", "Rejected", "Withdrawn") else "Yes",
        "Final disposition" if final_status in ("Approved", "Rejected", "Withdrawn") else "Current workflow status"
    )

# ---------------------------------------------------------------------------
# Intentional raw-data quality injections
# ---------------------------------------------------------------------------
quality_issues = []

def add_issue(table, issue_type, record_id, field, detail, expected_treatment):
    quality_issues.append({
        "Table": table,
        "Issue_Type": issue_type,
        "Record_ID": record_id,
        "Field": field,
        "Detail": detail,
        "Expected_Process_Treatment": expected_treatment,
    })

# Category variants.
for row in rng.sample(rfis, 24):
    original = row["Discipline"]
    variants = {
        "Electrical": "electrical ", "Mechanical": "MECH", "Architectural": "Arch.",
        "Structural": "STRUCTURAL", "Fire Protection": "Fire Prot.",
        "Specialty Systems": "Specialty"
    }
    if original in variants:
        row["Discipline"] = variants[original]
        add_issue("RFI Log", "Categorical standardization", row["RFI_ID"], "Discipline",
                  f"Variant of {original}", "Standardize to controlled value.")

for row in rng.sample(change_orders, 20):
    original = row["Change_Category"]
    variants = {
        "Owner-Directed Change": "Owner Directed", "Design Error or Omission": "Design E&O",
        "Unforeseen Condition": "Unforeseen Conditions", "Value Engineering": "VE",
        "Code or Regulatory Requirement": "Code / Regulatory"
    }
    if original in variants:
        row["Change_Category"] = variants[original]
        add_issue("Change Orders", "Categorical standardization", row["Change_Order_ID"], "Change_Category",
                  f"Variant of {original}", "Standardize to controlled value.")

for row in rng.sample(projects, 6):
    original = row["Delivery_Method"]
    variants = {"Design-Bid-Build": "DBB", "Design-Build": "Design Build", "CMAR": "CM at Risk", "IPD": "Integrated Project Delivery"}
    row["Delivery_Method"] = variants[original]
    add_issue("Projects", "Categorical standardization", row["Project_ID"], "Delivery_Method",
              f"Variant of {original}", "Standardize to controlled value.")

# Missing critical values.
closed_rfis = [r for r in rfis if r["RFI_Status"] in ("Closed", "Answered") and r["Final_Response_Date"]]
for row in rng.sample(closed_rfis, 6):
    row["Final_Response_Date"] = ""
    add_issue("RFI Log", "Missing critical value", row["RFI_ID"], "Final_Response_Date",
              "Closed/answered RFI missing final response date.", "Reconstruct from workflow event when unambiguous.")

approved_cos = [c for c in change_orders if c["Change_Status"] == "Approved" and c["Approved_Value"] != ""]
for row in rng.sample(approved_cos, 4):
    row["Approved_Value"] = ""
    add_issue("Change Orders", "Missing critical value", row["Change_Order_ID"], "Approved_Value",
              "Approved change missing approved value.", "Reconstruct from final negotiated value when evidence is consistent.")

for row in rng.sample(events, 3):
    row["Action_By_Role"] = ""
    add_issue("Workflow Events", "Missing value", row["Event_ID"], "Action_By_Role",
              "Workflow event missing action role.", "Infer only from adjacent documented transition when unambiguous; otherwise mark Unknown.")

# Invalid dates.
date_rfis = [r for r in rfis if r["Final_Response_Date"]]
for row in rng.sample(date_rfis, 5):
    submitted = date.fromisoformat(row["Submitted_Date"])
    row["Final_Response_Date"] = iso(submitted - timedelta(days=rng.randint(1, 5)))
    add_issue("RFI Log", "Invalid date sequence", row["RFI_ID"], "Final_Response_Date",
              "Final response occurs before submission.", "Repair using workflow event or quarantine if evidence conflicts.")

date_cos = [c for c in change_orders if c["Change_Status"] == "Approved" and c["Approved_Date"]]
for row in rng.sample(date_cos, 4):
    submitted = date.fromisoformat(row["Submitted_Date"])
    row["Approved_Date"] = iso(submitted - timedelta(days=rng.randint(1, 8)))
    add_issue("Change Orders", "Invalid date sequence", row["Change_Order_ID"], "Approved_Date",
              "Approval occurs before submission.", "Repair using final approval workflow event.")

# Numeric anomalies.
impact_rfis = [r for r in rfis if r["Actual_Cost_Impact"] not in (0, "")]
for row in rng.sample(impact_rfis, 3):
    row["Actual_Cost_Impact"] = -abs(row["Actual_Cost_Impact"])
    add_issue("RFI Log", "Invalid numeric value", row["RFI_ID"], "Actual_Cost_Impact",
              "Negative cost impact on a record marked as positive impact.", "Review sign convention and correct to positive impact amount.")

for row in rng.sample(change_orders, 2):
    row["Requested_Schedule_Days"] = -abs(int(row["Requested_Schedule_Days"] or rng.randint(1, 10)))
    add_issue("Change Orders", "Invalid numeric value", row["Change_Order_ID"], "Requested_Schedule_Days",
              "Negative requested schedule days.", "Correct sign when supporting fields confirm an extension request.")

# Invalid parent relationships.
for row in rng.sample(rfis, 2):
    row["Project_ID"] = "PRJ-999"
    add_issue("RFI Log", "Invalid foreign key", row["RFI_ID"], "Project_ID",
              "Project_ID does not exist in Projects.", "Quarantine record; do not guess parent.")

for row in rng.sample(change_orders, 1):
    row["Project_ID"] = "PRJ-998"
    add_issue("Change Orders", "Invalid foreign key", row["Change_Order_ID"], "Project_ID",
              "Project_ID does not exist in Projects.", "Quarantine record; do not guess parent.")

for row in rng.sample(events, 2):
    row["Project_ID"] = "PRJ-997"
    add_issue("Workflow Events", "Invalid foreign key", row["Event_ID"], "Project_ID",
              "Project_ID does not exist in Projects.", "Quarantine record; do not guess parent.")

for row in rng.sample(links, 2):
    row["RFI_ID"] = "RFI-99999"
    add_issue("RFI Change Links", "Invalid foreign key", row["Link_ID"], "RFI_ID",
              "RFI_ID does not exist in RFI Log.", "Quarantine link record.")

# Exact duplicates appended.
duplicate_plan = [
    ("Projects", projects, 2, "Project_ID"),
    ("RFI Log", rfis, 8, "RFI_ID"),
    ("Change Orders", change_orders, 5, "Change_Order_ID"),
    ("Workflow Events", events, 10, "Event_ID"),
    ("RFI Change Links", links, 3, "Link_ID"),
]
for table, rows, count, id_field in duplicate_plan:
    samples = rng.sample(rows, count)
    for sample in samples:
        rows.append(dict(sample))
        add_issue(table, "Exact duplicate", sample[id_field], id_field,
                  "Exact duplicate row appended to raw dataset.", "Remove duplicate while retaining one canonical record.")

# ---------------------------------------------------------------------------
# Write outputs
# ---------------------------------------------------------------------------
project_headers = [
    "Project_ID", "Project_Name", "Project_Type", "City", "State", "Region",
    "Client_Type", "Contract_Type", "Delivery_Method", "Complexity_Level",
    "Digital_Coordination_Level", "Owner_Decision_Profile", "Original_Budget",
    "Original_Contingency", "Planned_Start_Date", "Planned_End_Date",
    "Actual_Start_Date", "Forecast_End_Date", "Project_Status", "Current_Phase",
    "Project_Manager_ID", "Design_Manager_ID", "Change_Manager_ID"
]
rfi_headers = [
    "RFI_ID", "Project_ID", "RFI_Number", "RFI_Title", "Discipline", "Priority",
    "RFI_Type", "Submitted_Date", "Required_Response_Date", "First_Response_Date",
    "Final_Response_Date", "Closed_Date", "RFI_Status", "Submitted_By_Role",
    "Responsible_Role", "Revision_Count", "Reopen_Count", "Cost_Impact_Flag",
    "Estimated_Cost_Impact", "Actual_Cost_Impact", "Schedule_Impact_Flag",
    "Estimated_Schedule_Days", "Actual_Schedule_Days", "Field_Work_Affected",
    "Drawing_Reference_Count", "Response_Quality_Rating"
]
co_headers = [
    "Change_Order_ID", "Project_ID", "Change_Number", "Change_Title",
    "Change_Category", "Initiating_Party", "Discipline", "Change_Type",
    "Originating_Source", "Identified_Date", "Submitted_Date",
    "Required_Decision_Date", "First_Decision_Date", "Approved_Date",
    "Closed_Date", "Change_Status", "Submitted_Value", "Negotiated_Value",
    "Approved_Value", "Requested_Schedule_Days", "Approved_Schedule_Days",
    "Revision_Count", "Pricing_Status", "Authorization_Type",
    "Forecast_Incorporated_Date", "Cost_Code_Group"
]
event_headers = [
    "Event_ID", "Project_ID", "Item_Type", "Item_ID", "Event_Sequence",
    "Event_Timestamp", "From_Status", "To_Status", "Action_By_Role",
    "Assigned_To_Role", "Event_Action", "Revision_Number",
    "Decision_Required_Flag", "Comment_Category"
]
link_headers = [
    "Link_ID", "Project_ID", "RFI_ID", "Change_Order_ID", "Link_Type",
    "Link_Confidence", "Relationship_Date", "Relationship_Notes_Category"
]
quality_headers = [
    "Table", "Issue_Type", "Record_ID", "Field", "Detail",
    "Expected_Process_Treatment"
]

write_csv(RAW_DIR / "projects_raw.csv", projects, project_headers)
write_csv(RAW_DIR / "rfi_log_raw.csv", rfis, rfi_headers)
write_csv(RAW_DIR / "change_orders_raw.csv", change_orders, co_headers)
write_csv(RAW_DIR / "workflow_events_raw.csv", events, event_headers)
write_csv(RAW_DIR / "rfi_change_links_raw.csv", links, link_headers)
write_csv(DOC_DIR / "known_raw_data_quality_issues.csv", quality_issues, quality_headers)

profile = {
    "random_seed": SEED,
    "data_cutoff": CUTOFF.isoformat(),
    "intended_unique_records_before_quality_injections": {
        "projects": 90,
        "rfi_log": 3320,
        "change_orders": 1120,
        "workflow_events": event_counter - 1,
        "rfi_change_links": 680,
    },
    "raw_file_rows_after_injections": {
        "projects": len(projects),
        "rfi_log": len(rfis),
        "change_orders": len(change_orders),
        "workflow_events": len(events),
        "rfi_change_links": len(links),
    },
    "known_issue_count": len(quality_issues),
    "known_issue_types": {},
}
for issue in quality_issues:
    profile["known_issue_types"][issue["Issue_Type"]] = profile["known_issue_types"].get(issue["Issue_Type"], 0) + 1

(DOC_DIR / "raw_dataset_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
print(json.dumps(profile, indent=2))
