from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data' / 'raw'
CLEAN = ROOT / 'data' / 'cleaned'
PROCESSED = ROOT / 'data' / 'processed'
DOC = ROOT / 'documentation'
SQL = ROOT / 'sql'

for directory in (CLEAN, PROCESSED, DOC, SQL):
    directory.mkdir(parents=True, exist_ok=True)

CUTOFF = date(2025, 12, 31)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], headers: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if headers is None:
        headers = list(rows[0].keys()) if rows else []
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def date_text(value: date | datetime | None) -> str:
    if value is None:
        return ''
    if isinstance(value, datetime):
        return value.isoformat(timespec='minutes')
    return value.isoformat()


def numeric_text(value: float | int | None) -> str:
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def dedupe(rows: list[dict[str, str]], table: str, key: str, log: list[dict]) -> list[dict[str, str]]:
    seen: set[str] = set()
    output: list[dict[str, str]] = []
    for row in rows:
        record_id = row.get(key, '')
        if record_id in seen:
            log.append({
                'Action_ID': f'ACT-{len(log)+1:04d}',
                'Table': table,
                'Record_ID': record_id,
                'Field': key,
                'Issue_Type': 'Exact duplicate',
                'Raw_Value': record_id,
                'Clean_Value': '',
                'Action': 'Removed duplicate row',
                'Evidence': 'Exact duplicate primary key and identical row retained once',
                'Disposition': 'Removed',
            })
            continue
        seen.add(record_id)
        output.append(dict(row))
    return output


def log_change(log: list[dict], table: str, record_id: str, field: str, issue: str,
               raw_value: str, clean_value: str, action: str, evidence: str,
               disposition: str = 'Repaired') -> None:
    log.append({
        'Action_ID': f'ACT-{len(log)+1:04d}',
        'Table': table,
        'Record_ID': record_id,
        'Field': field,
        'Issue_Type': issue,
        'Raw_Value': raw_value,
        'Clean_Value': clean_value,
        'Action': action,
        'Evidence': evidence,
        'Disposition': disposition,
    })


def quarantine_record(quarantine: list[dict], table: str, record_id: str, reason: str,
                      source_issue: str, row: dict[str, str]) -> None:
    quarantine.append({
        'Quarantine_ID': f'Q-{len(quarantine)+1:04d}',
        'Table': table,
        'Record_ID': record_id,
        'Reason': reason,
        'Source_Issue': source_issue,
        'Raw_Record_JSON': json.dumps(row, sort_keys=True),
    })


projects_raw = read_csv(RAW / 'projects_raw.csv')
rfis_raw = read_csv(RAW / 'rfi_log_raw.csv')
changes_raw = read_csv(RAW / 'change_orders_raw.csv')
events_raw = read_csv(RAW / 'workflow_events_raw.csv')
links_raw = read_csv(RAW / 'rfi_change_links_raw.csv')
known_issues = read_csv(DOC / 'known_raw_data_quality_issues.csv')

cleaning_log: list[dict] = []
quarantine: list[dict] = []

projects = dedupe(projects_raw, 'Projects', 'Project_ID', cleaning_log)
rfis = dedupe(rfis_raw, 'RFI Log', 'RFI_ID', cleaning_log)
changes = dedupe(changes_raw, 'Change Orders', 'Change_Order_ID', cleaning_log)
events = dedupe(events_raw, 'Workflow Events', 'Event_ID', cleaning_log)
links = dedupe(links_raw, 'RFI Change Links', 'Link_ID', cleaning_log)

project_map = {row['Project_ID']: row for row in projects}
rfi_map = {row['RFI_ID']: row for row in rfis}
change_map = {row['Change_Order_ID']: row for row in changes}
event_map = {row['Event_ID']: row for row in events}

# Controlled-value mappings.
delivery_map = {
    'DBB': 'Design-Bid-Build',
    'Design Build': 'Design-Build',
    'CM at Risk': 'CMAR',
    'Integrated Project Delivery': 'IPD',
}
rfi_discipline_map = {
    'STRUCTURAL': 'Structural',
    'MECH': 'Mechanical',
    'electrical ': 'Electrical',
    'Arch.': 'Architectural',
    'Specialty': 'Specialty Systems',
    'Fire Prot.': 'Fire Protection',
}
change_category_map = {
    'Owner Directed': 'Owner-Directed Change',
    'Design E&O': 'Design Error or Omission',
    'Unforeseen Conditions': 'Unforeseen Condition',
    'VE': 'Value Engineering',
    'Code / Regulatory': 'Code or Regulatory Requirement',
}

for row in projects:
    old = row['Delivery_Method']
    if old in delivery_map:
        row['Delivery_Method'] = delivery_map[old]
        log_change(cleaning_log, 'Projects', row['Project_ID'], 'Delivery_Method',
                   'Categorical standardization', old, row['Delivery_Method'],
                   'Mapped to controlled delivery-method value',
                   'Controlled-value dictionary')

for row in rfis:
    old = row['Discipline']
    if old in rfi_discipline_map:
        row['Discipline'] = rfi_discipline_map[old]
        log_change(cleaning_log, 'RFI Log', row['RFI_ID'], 'Discipline',
                   'Categorical standardization', old, row['Discipline'],
                   'Mapped to controlled discipline value',
                   'Controlled-value dictionary')

for row in changes:
    old = row['Change_Category']
    if old in change_category_map:
        row['Change_Category'] = change_category_map[old]
        log_change(cleaning_log, 'Change Orders', row['Change_Order_ID'], 'Change_Category',
                   'Categorical standardization', old, row['Change_Category'],
                   'Mapped to controlled change-category value',
                   'Controlled-value dictionary')

# Rebuild maps after standardization.
project_map = {row['Project_ID']: row for row in projects}
rfi_map = {row['RFI_ID']: row for row in rfis}
change_map = {row['Change_Order_ID']: row for row in changes}
events_by_item: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in events:
    events_by_item[row['Item_ID']].append(row)
for item_events in events_by_item.values():
    item_events.sort(key=lambda x: (int(x['Event_Sequence']), x['Event_Timestamp']))

# Evidence-based RFI repairs.
for issue in known_issues:
    if issue['Table'] != 'RFI Log' or issue['Issue_Type'] not in {'Missing critical value', 'Invalid date sequence', 'Invalid numeric value'}:
        continue
    rid = issue['Record_ID']
    row = rfi_map.get(rid)
    if not row:
        continue
    field = issue['Field']
    old = row.get(field, '')
    if field == 'Final_Response_Date':
        final_events = [e for e in events_by_item.get(rid, []) if e['To_Status'] in {'Answered', 'Closed'}]
        if not final_events:
            continue
        repaired = parse_datetime(final_events[-1]['Event_Timestamp']).date().isoformat()
        row[field] = repaired
        log_change(cleaning_log, 'RFI Log', rid, field, issue['Issue_Type'], old, repaired,
                   'Reconstructed final response date',
                   f"Final workflow event {final_events[-1]['Event_ID']} at {final_events[-1]['Event_Timestamp']}")
    elif field == 'Actual_Cost_Impact':
        repaired = numeric_text(abs(float(old)))
        row[field] = repaired
        log_change(cleaning_log, 'RFI Log', rid, field, issue['Issue_Type'], old, repaired,
                   'Corrected sign to positive impact amount',
                   'Cost_Impact_Flag = Yes and dataset uses positive impact convention')

# Evidence-based change repairs.
for issue in known_issues:
    if issue['Table'] != 'Change Orders' or issue['Issue_Type'] not in {'Missing critical value', 'Invalid date sequence', 'Invalid numeric value'}:
        continue
    cid = issue['Record_ID']
    row = change_map.get(cid)
    if not row:
        continue
    field = issue['Field']
    old = row.get(field, '')
    if field == 'Approved_Value':
        repaired = row['Negotiated_Value']
        row[field] = repaired
        log_change(cleaning_log, 'Change Orders', cid, field, issue['Issue_Type'], old, repaired,
                   'Reconstructed approved value from final negotiated value',
                   'Approved status, final pricing status, and populated negotiated value')
    elif field == 'Approved_Date':
        approval_events = [e for e in events_by_item.get(cid, []) if e['To_Status'] == 'Approved']
        if not approval_events:
            continue
        repaired = parse_datetime(approval_events[-1]['Event_Timestamp']).date().isoformat()
        row[field] = repaired
        log_change(cleaning_log, 'Change Orders', cid, field, issue['Issue_Type'], old, repaired,
                   'Reconstructed approval date',
                   f"Final approval workflow event {approval_events[-1]['Event_ID']} at {approval_events[-1]['Event_Timestamp']}")
        # Preserve sequence validity when a previously generated close date now falls before repaired approval.
        closed = parse_date(row.get('Closed_Date'))
        repaired_date = parse_date(repaired)
        if closed and repaired_date and closed < repaired_date:
            old_closed = row['Closed_Date']
            row['Closed_Date'] = repaired
            log_change(cleaning_log, 'Change Orders', cid, 'Closed_Date', 'Derived date consistency',
                       old_closed, repaired, 'Aligned close date to repaired approval date',
                       'Closed date cannot precede approved date')
    elif field == 'Requested_Schedule_Days':
        repaired = numeric_text(abs(int(float(old))))
        row[field] = repaired
        log_change(cleaning_log, 'Change Orders', cid, field, issue['Issue_Type'], old, repaired,
                   'Corrected sign to nonnegative requested extension',
                   'Change record uses extension-day convention')

# Missing workflow action roles.
for issue in known_issues:
    if issue['Table'] != 'Workflow Events' or issue['Issue_Type'] != 'Missing value':
        continue
    eid = issue['Record_ID']
    row = event_map.get(eid)
    if not row:
        continue
    parent = rfi_map.get(row['Item_ID']) if row['Item_Type'] == 'RFI' else change_map.get(row['Item_ID'])
    inferred = 'Unknown'
    evidence = 'No unambiguous adjacent-role evidence'
    if parent:
        if row['Item_Type'] == 'RFI' and row['To_Status'] == 'Submitted':
            inferred = parent['Submitted_By_Role']
            evidence = 'RFI submission event matched Submitted_By_Role'
        elif row['Item_Type'] == 'RFI' and row['To_Status'] in {'Answered', 'Closed', 'Returned for Clarification'}:
            inferred = parent['Responsible_Role']
            evidence = 'RFI response/return event matched Responsible_Role'
        elif row['Item_Type'] == 'Change Order' and row['To_Status'] == 'Identified':
            inferred = 'Project Manager'
            evidence = 'Controlled workflow transition rule'
        elif row['Item_Type'] == 'Change Order' and row['To_Status'] == 'Submitted':
            inferred = 'Cost Manager'
            evidence = 'Controlled workflow transition rule'
        elif row['Item_Type'] == 'Change Order':
            inferred = 'Owner Representative'
            evidence = 'Controlled decision-workflow transition rule'
    old = row['Action_By_Role']
    row['Action_By_Role'] = inferred
    log_change(cleaning_log, 'Workflow Events', eid, 'Action_By_Role', 'Missing value', old, inferred,
               'Inferred workflow action role' if inferred != 'Unknown' else 'Assigned Unknown', evidence)

# Quarantine invalid parent records identified in the issue register.
invalid_rfi_ids = {i['Record_ID'] for i in known_issues if i['Table'] == 'RFI Log' and i['Issue_Type'] == 'Invalid foreign key'}
invalid_change_ids = {i['Record_ID'] for i in known_issues if i['Table'] == 'Change Orders' and i['Issue_Type'] == 'Invalid foreign key'}
invalid_event_ids = {i['Record_ID'] for i in known_issues if i['Table'] == 'Workflow Events' and i['Issue_Type'] == 'Invalid foreign key'}
invalid_link_ids = {i['Record_ID'] for i in known_issues if i['Table'] == 'RFI Change Links' and i['Issue_Type'] == 'Invalid foreign key'}

kept_rfis = []
for row in rfis:
    if row['RFI_ID'] in invalid_rfi_ids or row['Project_ID'] not in project_map:
        reason = f"Project_ID {row['Project_ID']} does not exist in Projects"
        quarantine_record(quarantine, 'RFI Log', row['RFI_ID'], reason, 'Invalid foreign key', row)
        log_change(cleaning_log, 'RFI Log', row['RFI_ID'], 'Project_ID', 'Invalid foreign key',
                   row['Project_ID'], '', 'Quarantined record', reason, 'Quarantined')
    else:
        kept_rfis.append(row)
rfis = kept_rfis
rfi_map = {row['RFI_ID']: row for row in rfis}

kept_changes = []
for row in changes:
    if row['Change_Order_ID'] in invalid_change_ids or row['Project_ID'] not in project_map:
        reason = f"Project_ID {row['Project_ID']} does not exist in Projects"
        quarantine_record(quarantine, 'Change Orders', row['Change_Order_ID'], reason, 'Invalid foreign key', row)
        log_change(cleaning_log, 'Change Orders', row['Change_Order_ID'], 'Project_ID', 'Invalid foreign key',
                   row['Project_ID'], '', 'Quarantined record', reason, 'Quarantined')
    else:
        kept_changes.append(row)
changes = kept_changes
change_map = {row['Change_Order_ID']: row for row in changes}

kept_events = []
for row in events:
    item_exists = (row['Item_Type'] == 'RFI' and row['Item_ID'] in rfi_map) or (
        row['Item_Type'] == 'Change Order' and row['Item_ID'] in change_map
    )
    parent_project = None
    if row['Item_Type'] == 'RFI' and row['Item_ID'] in rfi_map:
        parent_project = rfi_map[row['Item_ID']]['Project_ID']
    elif row['Item_Type'] == 'Change Order' and row['Item_ID'] in change_map:
        parent_project = change_map[row['Item_ID']]['Project_ID']
    direct_invalid = row['Event_ID'] in invalid_event_ids or row['Project_ID'] not in project_map
    cross_invalid = not item_exists or (parent_project is not None and row['Project_ID'] != parent_project)
    if direct_invalid or cross_invalid:
        if direct_invalid:
            reason = f"Project_ID {row['Project_ID']} does not exist in Projects"
            source = 'Invalid foreign key'
        elif not item_exists:
            reason = f"Item_ID {row['Item_ID']} was quarantined or does not exist"
            source = 'Cascading referential integrity'
        else:
            reason = f"Event Project_ID {row['Project_ID']} does not match item parent Project_ID {parent_project}"
            source = 'Cross-record consistency'
        quarantine_record(quarantine, 'Workflow Events', row['Event_ID'], reason, source, row)
        log_change(cleaning_log, 'Workflow Events', row['Event_ID'], 'Project_ID / Item_ID', source,
                   f"{row['Project_ID']} / {row['Item_ID']}", '', 'Quarantined record', reason, 'Quarantined')
    else:
        kept_events.append(row)
events = kept_events

kept_links = []
for row in links:
    project_exists = row['Project_ID'] in project_map
    rfi_exists = row['RFI_ID'] in rfi_map
    change_exists = row['Change_Order_ID'] in change_map
    project_consistent = (
        rfi_exists and change_exists
        and rfi_map[row['RFI_ID']]['Project_ID'] == row['Project_ID']
        and change_map[row['Change_Order_ID']]['Project_ID'] == row['Project_ID']
    )
    if row['Link_ID'] in invalid_link_ids or not project_exists or not rfi_exists or not change_exists or not project_consistent:
        reason_parts = []
        if not project_exists:
            reason_parts.append('project missing')
        if not rfi_exists:
            reason_parts.append('RFI missing or quarantined')
        if not change_exists:
            reason_parts.append('change missing or quarantined')
        if rfi_exists and change_exists and not project_consistent:
            reason_parts.append('cross-project mismatch')
        reason = '; '.join(reason_parts) or 'Known invalid foreign key'
        source = 'Invalid foreign key' if row['Link_ID'] in invalid_link_ids else 'Cascading referential integrity'
        quarantine_record(quarantine, 'RFI Change Links', row['Link_ID'], reason, source, row)
        log_change(cleaning_log, 'RFI Change Links', row['Link_ID'], 'Project_ID / RFI_ID / Change_Order_ID',
                   source, f"{row['Project_ID']} / {row['RFI_ID']} / {row['Change_Order_ID']}", '',
                   'Quarantined record', reason, 'Quarantined')
    else:
        kept_links.append(row)
links = kept_links

# Normalize event sequences to chronological order when the raw sequence conflicts with timestamps.
chronological_groups = defaultdict(list)
for row in events:
    chronological_groups[(row['Item_Type'], row['Item_ID'])].append(row)
for (item_type, item_id), item_events in chronological_groups.items():
    by_sequence = sorted(item_events, key=lambda x: (int(x['Event_Sequence']), x['Event_Timestamp']))
    timestamps = [parse_datetime(e['Event_Timestamp']) for e in by_sequence]
    if any(timestamps[i] < timestamps[i-1] for i in range(1, len(timestamps))):
        by_time = sorted(item_events, key=lambda x: (x['Event_Timestamp'], int(x['Event_Sequence']), x['Event_ID']))
        for new_sequence, event in enumerate(by_time, start=1):
            old_sequence = event['Event_Sequence']
            if int(old_sequence) != new_sequence:
                event['Event_Sequence'] = str(new_sequence)
                log_change(
                    cleaning_log, 'Workflow Events', event['Event_ID'], 'Event_Sequence',
                    'Discovered sequence inconsistency', old_sequence, str(new_sequence),
                    'Renumbered event sequence by timestamp',
                    f"Chronological normalization for {item_type} {item_id}"
                )

# Normalize basic whitespace and blank representation.
for table_rows in (projects, rfis, changes, events, links):
    for row in table_rows:
        for key, value in list(row.items()):
            if isinstance(value, str):
                row[key] = value.strip()

# Build event durations for technical process analysis.
events_by_item = defaultdict(list)
for row in events:
    events_by_item[(row['Item_Type'], row['Item_ID'])].append(row)
workflow_durations: list[dict] = []
for (item_type, item_id), item_events in events_by_item.items():
    item_events.sort(key=lambda x: (int(x['Event_Sequence']), x['Event_Timestamp']))
    for idx, event in enumerate(item_events):
        previous = item_events[idx - 1] if idx > 0 else None
        current_ts = parse_datetime(event['Event_Timestamp'])
        previous_ts = parse_datetime(previous['Event_Timestamp']) if previous else None
        hours = round((current_ts - previous_ts).total_seconds() / 3600, 2) if previous_ts else 0
        workflow_durations.append({
            'Event_ID': event['Event_ID'],
            'Project_ID': event['Project_ID'],
            'Item_Type': item_type,
            'Item_ID': item_id,
            'Event_Sequence': event['Event_Sequence'],
            'Event_Timestamp': event['Event_Timestamp'],
            'Previous_Event_Timestamp': previous['Event_Timestamp'] if previous else '',
            'From_Status': event['From_Status'],
            'To_Status': event['To_Status'],
            'Action_By_Role': event['Action_By_Role'],
            'Assigned_To_Role': event['Assigned_To_Role'],
            'Stage_Duration_Hours': hours,
            'Stage_Duration_Days': round(hours / 24, 2),
            'Handoff_Flag': 'Yes' if previous and previous['Assigned_To_Role'] != event['Assigned_To_Role'] else 'No',
            'Revision_Loop_Flag': 'Yes' if event['To_Status'] in {'Returned for Clarification', 'Returned for Revision'} else 'No',
        })

# Clean outputs.
write_csv(CLEAN / 'projects_clean.csv', projects, list(projects_raw[0].keys()))
write_csv(CLEAN / 'rfi_log_clean.csv', rfis, list(rfis_raw[0].keys()))
write_csv(CLEAN / 'change_orders_clean.csv', changes, list(changes_raw[0].keys()))
write_csv(CLEAN / 'workflow_events_clean.csv', events, list(events_raw[0].keys()))
write_csv(CLEAN / 'rfi_change_links_clean.csv', links, list(links_raw[0].keys()))
write_csv(PROCESSED / 'workflow_event_durations.csv', workflow_durations)
write_csv(DOC / 'cleaning_log.csv', cleaning_log)
write_csv(DOC / 'quarantine_records.csv', quarantine)

# Validation checks.
project_ids = {r['Project_ID'] for r in projects}
rfi_ids = {r['RFI_ID'] for r in rfis}
change_ids = {r['Change_Order_ID'] for r in changes}
event_ids = {r['Event_ID'] for r in events}
link_ids = {r['Link_ID'] for r in links}

checks: list[dict] = []
def add_check(check_id: str, category: str, description: str, failed_count: int, details: str = ''):
    checks.append({
        'Check_ID': check_id,
        'Category': category,
        'Description': description,
        'Failed_Count': failed_count,
        'Status': 'Passed' if failed_count == 0 else 'Failed',
        'Details': details,
    })

add_check('PK-01', 'Primary key', 'Projects Project_ID unique', len(projects) - len(project_ids))
add_check('PK-02', 'Primary key', 'RFI_ID unique', len(rfis) - len(rfi_ids))
add_check('PK-03', 'Primary key', 'Change_Order_ID unique', len(changes) - len(change_ids))
add_check('PK-04', 'Primary key', 'Event_ID unique', len(events) - len(event_ids))
add_check('PK-05', 'Primary key', 'Link_ID unique', len(links) - len(link_ids))
add_check('FK-01', 'Foreign key', 'RFI Project_ID exists', sum(r['Project_ID'] not in project_ids for r in rfis))
add_check('FK-02', 'Foreign key', 'Change Project_ID exists', sum(r['Project_ID'] not in project_ids for r in changes))
add_check('FK-03', 'Foreign key', 'Event Project_ID exists', sum(r['Project_ID'] not in project_ids for r in events))
add_check('FK-04', 'Foreign key', 'Link Project_ID exists', sum(r['Project_ID'] not in project_ids for r in links))
add_check('FK-05', 'Foreign key', 'Link RFI_ID exists', sum(r['RFI_ID'] not in rfi_ids for r in links))
add_check('FK-06', 'Foreign key', 'Link Change_Order_ID exists', sum(r['Change_Order_ID'] not in change_ids for r in links))
add_check('FK-07', 'Foreign key', 'Workflow Item_ID exists in selected item table', sum(not ((r['Item_Type']=='RFI' and r['Item_ID'] in rfi_ids) or (r['Item_Type']=='Change Order' and r['Item_ID'] in change_ids)) for r in events))
add_check('XR-01', 'Cross-record', 'Workflow Project_ID matches item parent', sum((r['Item_Type']=='RFI' and rfi_map[r['Item_ID']]['Project_ID'] != r['Project_ID']) or (r['Item_Type']=='Change Order' and change_map[r['Item_ID']]['Project_ID'] != r['Project_ID']) for r in events))
add_check('XR-02', 'Cross-record', 'Link project agrees with RFI and change', sum(rfi_map[r['RFI_ID']]['Project_ID'] != r['Project_ID'] or change_map[r['Change_Order_ID']]['Project_ID'] != r['Project_ID'] for r in links))

rfi_date_fail = 0
rfi_status_fail = 0
for r in rfis:
    submitted = parse_date(r['Submitted_Date'])
    required = parse_date(r['Required_Response_Date'])
    first = parse_date(r['First_Response_Date'])
    final = parse_date(r['Final_Response_Date'])
    closed = parse_date(r['Closed_Date'])
    if submitted and required and required < submitted:
        rfi_date_fail += 1
    if first and submitted and first < submitted:
        rfi_date_fail += 1
    if final and submitted and final < submitted:
        rfi_date_fail += 1
    if closed and final and closed < final:
        rfi_date_fail += 1
    if r['RFI_Status'] in {'Answered', 'Closed'} and not final:
        rfi_status_fail += 1
    if r['RFI_Status'] == 'Closed' and not closed:
        rfi_status_fail += 1
add_check('DT-01', 'Date', 'RFI date sequences valid', rfi_date_fail)
add_check('ST-01', 'Completeness', 'Answered/Closed RFIs have required final dates', rfi_status_fail)

change_date_fail = 0
change_status_fail = 0
for r in changes:
    identified = parse_date(r['Identified_Date'])
    submitted = parse_date(r['Submitted_Date'])
    required = parse_date(r['Required_Decision_Date'])
    first = parse_date(r['First_Decision_Date'])
    approved = parse_date(r['Approved_Date'])
    closed = parse_date(r['Closed_Date'])
    incorporated = parse_date(r['Forecast_Incorporated_Date'])
    if identified and submitted and submitted < identified:
        change_date_fail += 1
    if submitted and required and required < submitted:
        change_date_fail += 1
    if first and submitted and first < submitted:
        change_date_fail += 1
    if approved and submitted and approved < submitted:
        change_date_fail += 1
    if closed and approved and closed < approved:
        change_date_fail += 1
    if incorporated and approved and incorporated < approved:
        change_date_fail += 1
    if r['Change_Status'] == 'Approved' and (not approved or r['Approved_Value'] == ''):
        change_status_fail += 1
add_check('DT-02', 'Date', 'Change-order date sequences valid', change_date_fail)
add_check('ST-02', 'Completeness', 'Approved changes have approval date and value', change_status_fail)

numeric_fail = 0
for r in rfis:
    if float(r['Actual_Cost_Impact'] or 0) < 0 or int(float(r['Estimated_Schedule_Days'] or 0)) < 0 or int(float(r['Actual_Schedule_Days'] or 0)) < 0:
        numeric_fail += 1
    if not 1 <= int(r['Response_Quality_Rating']) <= 5:
        numeric_fail += 1
for r in changes:
    if int(float(r['Requested_Schedule_Days'] or 0)) < 0 or int(float(r['Approved_Schedule_Days'] or 0)) < 0:
        numeric_fail += 1
add_check('NM-01', 'Numeric', 'Impact values and ratings follow defined rules', numeric_fail)

controlled_fail = 0
valid_delivery = {'Design-Bid-Build', 'Design-Build', 'CMAR', 'IPD'}
valid_disciplines = {'Architectural','Structural','Mechanical','Electrical','Plumbing','Civil','Fire Protection','Controls','General','Specialty Systems'}
valid_categories = {'Owner-Directed Change','Design Error or Omission','Unforeseen Condition','Code or Regulatory Requirement','Value Engineering','Scope Clarification','Substitution','Schedule Acceleration','Quantity Variation'}
controlled_fail += sum(r['Delivery_Method'] not in valid_delivery for r in projects)
controlled_fail += sum(r['Discipline'] not in valid_disciplines for r in rfis)
controlled_fail += sum(r['Change_Category'] not in valid_categories for r in changes)
add_check('CV-01', 'Controlled values', 'Controlled categorical values standardized', controlled_fail)

sequence_fail = 0
for item_events in events_by_item.values():
    ordered = sorted(item_events, key=lambda x: int(x['Event_Sequence']))
    sequences = [int(e['Event_Sequence']) for e in ordered]
    timestamps = [parse_datetime(e['Event_Timestamp']) for e in ordered]
    if sequences != sorted(sequences) or any(timestamps[i] < timestamps[i-1] for i in range(1, len(timestamps))):
        sequence_fail += 1
add_check('DT-03', 'Date', 'Workflow event sequences and timestamps are nondecreasing', sequence_fail)
add_check('DT-04', 'Date', 'Workflow events do not exceed observed cutoff', sum(parse_datetime(r['Event_Timestamp']).date() > CUTOFF for r in events))

write_csv(DOC / 'data_quality_results.csv', checks)

# Row reconciliation.
reconciliation = [
    {
        'Table': 'Projects', 'Raw_Rows': len(projects_raw), 'Duplicate_Removals': len(projects_raw)-len({r['Project_ID'] for r in projects_raw}),
        'Quarantined_Rows': sum(q['Table']=='Projects' for q in quarantine), 'Clean_Rows': len(projects),
    },
    {
        'Table': 'RFI Log', 'Raw_Rows': len(rfis_raw), 'Duplicate_Removals': len(rfis_raw)-len({r['RFI_ID'] for r in rfis_raw}),
        'Quarantined_Rows': sum(q['Table']=='RFI Log' for q in quarantine), 'Clean_Rows': len(rfis),
    },
    {
        'Table': 'Change Orders', 'Raw_Rows': len(changes_raw), 'Duplicate_Removals': len(changes_raw)-len({r['Change_Order_ID'] for r in changes_raw}),
        'Quarantined_Rows': sum(q['Table']=='Change Orders' for q in quarantine), 'Clean_Rows': len(changes),
    },
    {
        'Table': 'Workflow Events', 'Raw_Rows': len(events_raw), 'Duplicate_Removals': len(events_raw)-len({r['Event_ID'] for r in events_raw}),
        'Quarantined_Rows': sum(q['Table']=='Workflow Events' for q in quarantine), 'Clean_Rows': len(events),
    },
    {
        'Table': 'RFI Change Links', 'Raw_Rows': len(links_raw), 'Duplicate_Removals': len(links_raw)-len({r['Link_ID'] for r in links_raw}),
        'Quarantined_Rows': sum(q['Table']=='RFI Change Links' for q in quarantine), 'Clean_Rows': len(links),
    },
]
for row in reconciliation:
    row['Reconciled'] = 'Yes' if row['Raw_Rows'] == row['Duplicate_Removals'] + row['Quarantined_Rows'] + row['Clean_Rows'] else 'No'
write_csv(DOC / 'row_reconciliation.csv', reconciliation)

# SQL database and analytical views.
db_path = PROCESSED / 'construction_change_order_rfi_analytics.sqlite'
if db_path.exists():
    db_path.unlink()
conn = sqlite3.connect(db_path)
conn.execute('PRAGMA foreign_keys = ON;')

schema_sql = '''
CREATE TABLE projects (
    Project_ID TEXT PRIMARY KEY,
    Project_Name TEXT NOT NULL,
    Project_Type TEXT NOT NULL,
    City TEXT NOT NULL,
    State TEXT NOT NULL,
    Region TEXT NOT NULL,
    Client_Type TEXT NOT NULL,
    Contract_Type TEXT NOT NULL,
    Delivery_Method TEXT NOT NULL,
    Complexity_Level TEXT NOT NULL,
    Digital_Coordination_Level TEXT NOT NULL,
    Owner_Decision_Profile TEXT NOT NULL,
    Original_Budget REAL NOT NULL,
    Original_Contingency REAL NOT NULL,
    Planned_Start_Date TEXT NOT NULL,
    Planned_End_Date TEXT NOT NULL,
    Actual_Start_Date TEXT NOT NULL,
    Forecast_End_Date TEXT NOT NULL,
    Project_Status TEXT NOT NULL,
    Current_Phase TEXT NOT NULL,
    Project_Manager_ID TEXT NOT NULL,
    Design_Manager_ID TEXT NOT NULL,
    Change_Manager_ID TEXT NOT NULL
);

CREATE TABLE rfi_log (
    RFI_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    RFI_Number TEXT NOT NULL,
    RFI_Title TEXT NOT NULL,
    Discipline TEXT NOT NULL,
    Priority TEXT NOT NULL,
    RFI_Type TEXT NOT NULL,
    Submitted_Date TEXT NOT NULL,
    Required_Response_Date TEXT NOT NULL,
    First_Response_Date TEXT,
    Final_Response_Date TEXT,
    Closed_Date TEXT,
    RFI_Status TEXT NOT NULL,
    Submitted_By_Role TEXT NOT NULL,
    Responsible_Role TEXT NOT NULL,
    Revision_Count INTEGER NOT NULL,
    Reopen_Count INTEGER NOT NULL,
    Cost_Impact_Flag TEXT NOT NULL,
    Estimated_Cost_Impact REAL NOT NULL,
    Actual_Cost_Impact REAL NOT NULL,
    Schedule_Impact_Flag TEXT NOT NULL,
    Estimated_Schedule_Days INTEGER NOT NULL,
    Actual_Schedule_Days INTEGER NOT NULL,
    Field_Work_Affected TEXT NOT NULL,
    Drawing_Reference_Count INTEGER NOT NULL,
    Response_Quality_Rating INTEGER NOT NULL
);

CREATE TABLE change_orders (
    Change_Order_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    Change_Number TEXT NOT NULL,
    Change_Title TEXT NOT NULL,
    Change_Category TEXT NOT NULL,
    Initiating_Party TEXT NOT NULL,
    Discipline TEXT NOT NULL,
    Change_Type TEXT NOT NULL,
    Originating_Source TEXT NOT NULL,
    Identified_Date TEXT NOT NULL,
    Submitted_Date TEXT NOT NULL,
    Required_Decision_Date TEXT NOT NULL,
    First_Decision_Date TEXT,
    Approved_Date TEXT,
    Closed_Date TEXT,
    Change_Status TEXT NOT NULL,
    Submitted_Value REAL NOT NULL,
    Negotiated_Value REAL,
    Approved_Value REAL,
    Requested_Schedule_Days INTEGER NOT NULL,
    Approved_Schedule_Days INTEGER NOT NULL,
    Revision_Count INTEGER NOT NULL,
    Pricing_Status TEXT NOT NULL,
    Authorization_Type TEXT NOT NULL,
    Forecast_Incorporated_Date TEXT,
    Cost_Code_Group TEXT NOT NULL
);

CREATE TABLE workflow_events (
    Event_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    Item_Type TEXT NOT NULL,
    Item_ID TEXT NOT NULL,
    Event_Sequence INTEGER NOT NULL,
    Event_Timestamp TEXT NOT NULL,
    From_Status TEXT,
    To_Status TEXT NOT NULL,
    Action_By_Role TEXT NOT NULL,
    Assigned_To_Role TEXT,
    Event_Action TEXT NOT NULL,
    Revision_Number INTEGER NOT NULL,
    Decision_Required_Flag TEXT NOT NULL,
    Comment_Category TEXT NOT NULL
);

CREATE TABLE rfi_change_links (
    Link_ID TEXT PRIMARY KEY,
    Project_ID TEXT NOT NULL REFERENCES projects(Project_ID),
    RFI_ID TEXT NOT NULL REFERENCES rfi_log(RFI_ID),
    Change_Order_ID TEXT NOT NULL REFERENCES change_orders(Change_Order_ID),
    Link_Type TEXT NOT NULL,
    Link_Confidence TEXT NOT NULL,
    Relationship_Date TEXT NOT NULL,
    Relationship_Notes_Category TEXT NOT NULL
);

CREATE TABLE cleaning_log (
    Action_ID TEXT PRIMARY KEY,
    Table_Name TEXT NOT NULL,
    Record_ID TEXT NOT NULL,
    Field_Name TEXT NOT NULL,
    Issue_Type TEXT NOT NULL,
    Raw_Value TEXT,
    Clean_Value TEXT,
    Action TEXT NOT NULL,
    Evidence TEXT,
    Disposition TEXT NOT NULL
);

CREATE TABLE quarantine_records (
    Quarantine_ID TEXT PRIMARY KEY,
    Table_Name TEXT NOT NULL,
    Record_ID TEXT NOT NULL,
    Reason TEXT NOT NULL,
    Source_Issue TEXT NOT NULL,
    Raw_Record_JSON TEXT NOT NULL
);
'''
conn.executescript(schema_sql)

project_cols = list(projects[0].keys())
rfi_cols = list(rfis[0].keys())
change_cols = list(changes[0].keys())
event_cols = list(events[0].keys())
link_cols = list(links[0].keys())

numeric_project = {'Original_Budget': float, 'Original_Contingency': float}
numeric_rfi = {'Revision_Count': int, 'Reopen_Count': int, 'Estimated_Cost_Impact': float, 'Actual_Cost_Impact': float,
               'Estimated_Schedule_Days': int, 'Actual_Schedule_Days': int, 'Drawing_Reference_Count': int, 'Response_Quality_Rating': int}
numeric_change = {'Submitted_Value': float, 'Negotiated_Value': float, 'Approved_Value': float,
                  'Requested_Schedule_Days': int, 'Approved_Schedule_Days': int, 'Revision_Count': int}
numeric_event = {'Event_Sequence': int, 'Revision_Number': int}

def db_values(row, cols, converters):
    output = []
    for col in cols:
        value = row[col]
        if col in converters:
            if value == '':
                output.append(None)
            else:
                output.append(converters[col](float(value)) if converters[col] is int else converters[col](value))
        else:
            output.append(value if value != '' else None)
    return output

for table, rows, cols, converters in [
    ('projects', projects, project_cols, numeric_project),
    ('rfi_log', rfis, rfi_cols, numeric_rfi),
    ('change_orders', changes, change_cols, numeric_change),
    ('workflow_events', events, event_cols, numeric_event),
    ('rfi_change_links', links, link_cols, {}),
]:
    placeholders = ','.join('?' for _ in cols)
    quoted_cols = ','.join(f'"{c}"' for c in cols)
    conn.executemany(f'INSERT INTO {table} ({quoted_cols}) VALUES ({placeholders})', [db_values(row, cols, converters) for row in rows])

conn.executemany(
    'INSERT INTO cleaning_log VALUES (?,?,?,?,?,?,?,?,?,?)',
    [(r['Action_ID'], r['Table'], r['Record_ID'], r['Field'], r['Issue_Type'], r['Raw_Value'], r['Clean_Value'], r['Action'], r['Evidence'], r['Disposition']) for r in cleaning_log]
)
conn.executemany(
    'INSERT INTO quarantine_records VALUES (?,?,?,?,?,?)',
    [(r['Quarantine_ID'], r['Table'], r['Record_ID'], r['Reason'], r['Source_Issue'], r['Raw_Record_JSON']) for r in quarantine]
)

views_sql = '''
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
'''
conn.executescript(views_sql)
conn.commit()

# Database integrity checks.
foreign_key_errors = conn.execute('PRAGMA foreign_key_check').fetchall()
quick_check = conn.execute('PRAGMA quick_check').fetchone()[0]
conn.close()

# Save SQL scripts.
(SQL / '01_create_clean_schema.sql').write_text(schema_sql.strip() + '\n', encoding='utf-8')
(SQL / '02_create_analysis_views.sql').write_text(views_sql.strip() + '\n', encoding='utf-8')
quality_sql = '''
-- Process-phase validation queries
SELECT 'Projects duplicate IDs' AS check_name, COUNT(*) AS failures
FROM (SELECT Project_ID FROM projects GROUP BY Project_ID HAVING COUNT(*) > 1)
UNION ALL
SELECT 'RFI orphan projects', COUNT(*) FROM rfi_log r LEFT JOIN projects p ON p.Project_ID=r.Project_ID WHERE p.Project_ID IS NULL
UNION ALL
SELECT 'Change orphan projects', COUNT(*) FROM change_orders c LEFT JOIN projects p ON p.Project_ID=c.Project_ID WHERE p.Project_ID IS NULL
UNION ALL
SELECT 'Link orphan RFIs', COUNT(*) FROM rfi_change_links l LEFT JOIN rfi_log r ON r.RFI_ID=l.RFI_ID WHERE r.RFI_ID IS NULL
UNION ALL
SELECT 'Link orphan changes', COUNT(*) FROM rfi_change_links l LEFT JOIN change_orders c ON c.Change_Order_ID=l.Change_Order_ID WHERE c.Change_Order_ID IS NULL
UNION ALL
SELECT 'Answered/closed RFIs missing final response', COUNT(*) FROM rfi_log WHERE RFI_Status IN ('Answered','Closed') AND Final_Response_Date IS NULL
UNION ALL
SELECT 'Approved changes missing approval date/value', COUNT(*) FROM change_orders WHERE Change_Status='Approved' AND (Approved_Date IS NULL OR Approved_Value IS NULL);
'''
(SQL / '03_process_validation_queries.sql').write_text(quality_sql.strip() + '\n', encoding='utf-8')

# Process report JSON.
report = {
    'phase': 'Process',
    'status': 'Passed' if all(c['Status'] == 'Passed' for c in checks) and not foreign_key_errors and quick_check == 'ok' and all(r['Reconciled']=='Yes' for r in reconciliation) else 'Review Required',
    'raw_rows': {name: len(rows) for name, rows in [('projects', projects_raw), ('rfi_log', rfis_raw), ('change_orders', changes_raw), ('workflow_events', events_raw), ('rfi_change_links', links_raw)]},
    'clean_rows': {name: len(rows) for name, rows in [('projects', projects), ('rfi_log', rfis), ('change_orders', changes), ('workflow_events', events), ('rfi_change_links', links)]},
    'duplicate_removals': sum(r['Disposition'] == 'Removed' for r in cleaning_log),
    'repaired_or_standardized_actions': sum(r['Disposition'] == 'Repaired' for r in cleaning_log),
    'quarantined_rows': len(quarantine),
    'cleaning_log_actions': len(cleaning_log),
    'quality_checks': len(checks),
    'passed_quality_checks': sum(c['Status'] == 'Passed' for c in checks),
    'foreign_key_errors': foreign_key_errors,
    'sqlite_quick_check': quick_check,
    'row_reconciliation_passed': all(r['Reconciled'] == 'Yes' for r in reconciliation),
}
(DOC / 'process_validation_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')

print(json.dumps(report, indent=2))
