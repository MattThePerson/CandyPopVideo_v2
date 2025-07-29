# Runs the python backend (fastApi)
$ErrorActionPreference = "Stop"

# Set backend port
$BACKEND_PORT = 8000

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..


# [DEV] Handle .ps1 script options
$forwardArgs = @()
$REINSTALL_VENV = 0
$env:DEV_MODE = "0"

foreach ($arg in $args) {
    if ($arg -eq "--use-new-frontend") {
        # Write-Host "[.ps1] Captured '--use-new-frontend' command"
        
    } elseif ($arg -eq "--dev") {
        Write-Host "[.ps1] Captured '--dev' command"
        $env:DEV_MODE = "1"
    } elseif ($arg -eq "--reinstall-venv") {
        Write-Host "[.ps1] Captured '--reinstall-venv' command"
        $REINSTALL_VENV = 1
    } else {
        $forwardArgs += $arg
    }
}


# Install venv
if (-Not (Test-Path ".venv\Scripts\activate.ps1") -or $REINSTALL_VENV -eq 1) {
    Write-Host "[.ps1] Creating python virtual environment (.venv) ..."
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    Write-Host "[.ps1] Done! Local environment created."
}


# Start uvicorn
Write-Host "[.ps1] Starting uvicorn on port $BACKEND_PORT and extra args: '$forwardArgs'"
& .\.venv\Scripts\uvicorn.exe python_src.main:app --host 0.0.0.0 --workers 1 --port $BACKEND_PORT @forwardArgs
