# Analysis

## Status

The Analyze phase is complete.

## Primary outputs

- `excel/construction_change_order_rfi_analysis.xlsx`
- `tables/executive_kpis.csv`
- `tables/project_workflow_risk_summary.csv`
- `tables/top_10_priority_projects.csv`
- `tables/rfi_discipline_summary.csv`
- `tables/rfi_type_summary.csv`
- `tables/change_category_summary.csv`
- `tables/workflow_bottleneck_summary.csv`
- `tables/lifecycle_segment_summary.csv`
- `tables/association_results.csv`
- `tables/exploratory_model_results.csv`

## Reproduction

Install:

```powershell
pip install -r analysis\requirements-analysis.txt
```

Run:

```powershell
python analysis\run_analysis.py
```

The script reads the validated SQLite database and refreshes the CSV analytical tables and validation summary.

## Interpretation controls

- All records are synthetic.
- Correlation does not establish causation.
- The project-risk score is transparent and deterministic.
- The exploratory logistic models are not approved for production use.
