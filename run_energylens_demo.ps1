# EnergyLens Demo Runner
# Installs dependencies, trains model, and analyzes examples

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$OutputDir = Join-Path $RepoRoot "demo_output"

# Create output directory
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "  EnergyLens AI - Demo Runner" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# Step 1: Activate venv
Write-Host "`n[1/5] Activating virtual environment..." -ForegroundColor Yellow
$VenvPath = Join-Path $RepoRoot "venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    Write-Host "[ERROR] venv activation script not found at: $ActivateScript" -ForegroundColor Red
    exit 1
}

& $ActivateScript
Write-Host "[OK] venv activated" -ForegroundColor Green

# Step 2: Install dependencies
Write-Host "`n[2/5] Installing dependencies..." -ForegroundColor Yellow
$RequirementsFile = Join-Path $RepoRoot "requirements.txt"

if (-not (Test-Path $RequirementsFile)) {
    Write-Host "[ERROR] requirements.txt not found at: $RequirementsFile" -ForegroundColor Red
    exit 1
}

pip install -r $RequirementsFile --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install requirements" -ForegroundColor Red
    exit 1
}

pip install -e . --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install package in editable mode" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Step 3: Train model
Write-Host "`n[3/5] Training ML model (100 samples)..." -ForegroundColor Yellow
Write-Host "       (This will take several minutes...)" -ForegroundColor Gray

$TrainLog = Join-Path $OutputDir "train_output.txt"
energylens train --samples 100 | Tee-Object -FilePath $TrainLog

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Training failed" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Training complete. Output saved to: $TrainLog" -ForegroundColor Green

# Step 4: Analyze bad_code.py
Write-Host "`n[4/5] Analyzing bad_code.py..." -ForegroundColor Yellow
$BadCodeAnalysis = Join-Path $OutputDir "bad_code_analysis.txt"
$BadCodePath = Join-Path $RepoRoot "examples\bad_code.py"

if (-not (Test-Path $BadCodePath)) {
    Write-Host "[ERROR] $BadCodePath not found" -ForegroundColor Red
    exit 1
}

energylens analyze $BadCodePath | Tee-Object -FilePath $BadCodeAnalysis
Write-Host "[OK] Analysis saved to: $BadCodeAnalysis" -ForegroundColor Green

# Step 5: Analyze good_code.py
Write-Host "`n[5/5] Analyzing good_code.py..." -ForegroundColor Yellow
$GoodCodeAnalysis = Join-Path $OutputDir "good_code_analysis.txt"
$GoodCodePath = Join-Path $RepoRoot "examples\good_code.py"

if (-not (Test-Path $GoodCodePath)) {
    Write-Host "[ERROR] $GoodCodePath not found" -ForegroundColor Red
    exit 1
}

energylens analyze $GoodCodePath | Tee-Object -FilePath $GoodCodeAnalysis
Write-Host "[OK] Analysis saved to: $GoodCodeAnalysis" -ForegroundColor Green

# Step 6: Run comparison
Write-Host "`n[BONUS] Running direct comparison..." -ForegroundColor Yellow
$ComparisonOutput = Join-Path $OutputDir "comparison.txt"
energylens compare $BadCodePath $GoodCodePath | Tee-Object -FilePath $ComparisonOutput
Write-Host "[OK] Comparison saved to: $ComparisonOutput" -ForegroundColor Green

# Summary
Write-Host "`n===============================================" -ForegroundColor Cyan
Write-Host "  Demo Complete!" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "`nOutput files saved to: $OutputDir" -ForegroundColor Green
Write-Host "  - train_output.txt" -ForegroundColor Cyan
Write-Host "  - bad_code_analysis.txt" -ForegroundColor Cyan
Write-Host "  - good_code_analysis.txt" -ForegroundColor Cyan
Write-Host "  - comparison.txt" -ForegroundColor Cyan
Write-Host ""
