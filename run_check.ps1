$ErrorActionPreference = "Stop"
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")

if (-not (Test-Path "$PSScriptRoot\contacts.csv")) {
    Copy-Item "$PSScriptRoot\contacts_template.csv" "$PSScriptRoot\contacts.csv"
}

python "$PSScriptRoot\zalo_csv_sender.py" "$PSScriptRoot\contacts.csv" --dry-run
