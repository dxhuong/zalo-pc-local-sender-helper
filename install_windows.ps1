$ErrorActionPreference = "Stop"

Write-Host "== Zalo PC CSV Sender setup =="

function Refresh-Path {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
}

Refresh-Path

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python -or $python.Source -like "*WindowsApps*") {
    Write-Host "Python was not found in PATH. Installing Python 3.12 with winget..."
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if (-not $winget) {
        throw "winget is not available. Install Python 3 manually from https://www.python.org/downloads/ and tick 'Add python.exe to PATH'."
    }
    winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements
    Refresh-Path
}

Write-Host "Python:"
python --version

Write-Host "Installing Python dependencies..."
python -m pip install -r "$PSScriptRoot\requirements.txt"

if (-not (Test-Path "$PSScriptRoot\contacts.csv")) {
    Copy-Item "$PSScriptRoot\contacts_template.csv" "$PSScriptRoot\contacts.csv"
    Write-Host "Created contacts.csv from contacts_template.csv"
}

Write-Host "Validating sample CSV..."
python "$PSScriptRoot\zalo_csv_sender.py" "$PSScriptRoot\contacts.csv" --dry-run

Write-Host ""
Write-Host "Setup complete."
Write-Host "Edit contacts.csv, open Zalo PC, then run one of:"
Write-Host "  .\run_confirm.ps1"
Write-Host "  .\run_auto_slow.ps1"
