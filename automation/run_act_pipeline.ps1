$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonScript = Join-Path $PSScriptRoot "generate_management_alerts.py"
$LogDir = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "act_pipeline_$Timestamp.log"

"Starting Project 2 Act automation at $(Get-Date)" | Tee-Object -FilePath $LogFile

python $PythonScript 2>&1 | Tee-Object -FilePath $LogFile -Append
if ($LASTEXITCODE -ne 0) {
    throw "Management alert generation failed."
}

"Completed successfully at $(Get-Date)" | Tee-Object -FilePath $LogFile -Append
