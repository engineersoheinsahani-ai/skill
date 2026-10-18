# =============================================================
#  Building Energy Forecasting Pipeline v8.1 - SETUP SCRIPT
#  Usage:  .\setup.ps1
# =============================================================

$ErrorActionPreference = "Stop"
$ROOT = "D:\نمونه کار\iman2\emp\A1\bullding\building_energy_pipeline"
if (-not (Test-Path $ROOT)) { New-Item -ItemType Directory -Force -Path $ROOT | Out-Null }
Set-Location $ROOT

Write-Host "[1/5] Creating folder structure..." -ForegroundColor Cyan
"src", "data", "logs", "tools", "tests",
"outputs", "outputs\figures", "outputs\tables", "outputs\models" |
  ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

Write-Host "[2/5] Copying scripts from the download folder..." -ForegroundColor Cyan
# Edit $DOWNLOADS to wherever you unzipped the scripts.
$DOWNLOADS = "$env:USERPROFILE\Downloads\pipeline_v81"
Copy-Item "$DOWNLOADS\src\*.py"   "$ROOT\src\"   -Force
Copy-Item "$DOWNLOADS\tools\*.py" "$ROOT\tools\" -Force
Copy-Item "$DOWNLOADS\tests\*.py" "$ROOT\tests\" -Force
Copy-Item "$DOWNLOADS\requirements.txt" "$ROOT\" -Force

Write-Host "[3/5] Installing Python dependencies..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r "$ROOT\requirements.txt"

Write-Host "[4/5] Verifying environment..." -ForegroundColor Cyan
python -c "import pandas, numpy, sklearn, xgboost, lightgbm, matplotlib, joblib, optuna, shap; print('  imports OK')"
python -m pytest "$ROOT\tests" -q

Write-Host "[5/5] Generating the auxiliary datasets (TMY3 + ResStock)..." -ForegroundColor Cyan
# Skip this step if you already have real TMY3 / ResStock files in .\data
python "$ROOT\tools\make_aux_data.py"
python "$ROOT\tools\calibrate_resstock_physics.py"

Write-Host ""
Write-Host "Setup complete. Next steps:" -ForegroundColor Green
Write-Host "  Smoke test : python src\main.py --fast --recs-nrows 4000 --resstock-nrows 6000 --n-seeds 3 --ensemble-seeds 1"
Write-Host "  Full run   : python src\main.py --n-seeds 10"
