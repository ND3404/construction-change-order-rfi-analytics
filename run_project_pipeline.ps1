$ErrorActionPreference = "Stop"

Write-Host "1/4 Generate raw synthetic data"
python data\generation\generate_synthetic_change_rfi_data.py

Write-Host "2/4 Clean, validate, and build SQLite"
python data\processing\process_clean_and_validate.py

Write-Host "3/4 Run analysis"
python analysis\run_analysis.py

Write-Host "4/4 Generate management alerts"
python automation\generate_management_alerts.py

Write-Host "Pipeline completed successfully."
