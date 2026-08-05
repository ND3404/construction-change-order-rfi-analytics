# Process and Validation Pipeline

Run from the project root:

```powershell
python data\processing\process_clean_and_validate.py
```

The script:

- removes exact duplicates;
- standardizes controlled categorical values;
- reconstructs missing or invalid dates from workflow evidence;
- reconstructs approved values from final negotiated values when supported;
- corrects documented numerical sign errors;
- infers missing workflow roles only when the transition evidence is unambiguous;
- quarantines invalid parent relationships and dependent orphan records;
- normalizes event sequence numbers when raw order conflicts with timestamps;
- writes five clean CSV files;
- builds the workflow-duration technical table;
- creates the SQLite database and analytical views;
- writes the cleaning log, quarantine register, quality results, and row reconciliation;
- and validates primary keys, foreign keys, dates, controlled values, and database integrity.

The raw files remain unchanged.
