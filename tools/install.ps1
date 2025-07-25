$ErrorActionPreference = "Stop"

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..



# Install venv
if (-Not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[.ps1] Creating python virtual environment (.venv) ..."
    python -m venv .venv
}
.\.venv\Scripts\Activate.ps1

Write-Host "[venv]"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 
Write-Host "[pyinstaller] Creating executable launcher"
pyinstaller tray_app/tray_app.py `
--onefile `
--noconsole --icon=assets/icon.ico `
--distpath . `
--name "CandyPopVideoTrayApp"
Remove-Item .\*.spec
Write-Host "[pyinstaller] Done"
