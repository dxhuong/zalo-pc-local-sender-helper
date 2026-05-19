$ErrorActionPreference = "Stop"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")

if (-not (Test-Path "$PSScriptRoot\contacts.csv")) {
    Copy-Item "$PSScriptRoot\contacts_template.csv" "$PSScriptRoot\contacts.csv"
    Write-Host "Created contacts.csv. Edit it before running again."
    exit 1
}

python "$PSScriptRoot\zalo_csv_sender.py" "$PSScriptRoot\contacts.csv" --start-now --auto-send --min-send-delay 20 --max-send-delay 45 --min-before-send-delay 2 --max-before-send-delay 6
