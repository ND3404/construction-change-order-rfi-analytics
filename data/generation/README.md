# Synthetic Data Generation

Run from the project root:

```powershell
python data\generation\generate_synthetic_change_rfi_data.py
```

The script uses Python's standard library and the deterministic seed `20260803`.

It creates the five raw CSV files plus:

- `documentation/known_raw_data_quality_issues.csv`
- `documentation/raw_dataset_profile.json`

The script intentionally adds controlled raw-data issues after constructing the valid base records. This supports the Process-phase cleaning and validation case study.
