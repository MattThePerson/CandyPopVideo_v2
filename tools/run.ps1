$ErrorActionPreference = "Stop"

# Set backend port
$BACKEND_PORT = 8000

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

# Check if .venv exists
if (-Not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[.ps1] No venv created, run tools\install.bat"
    exit 1
}

# [DEV] Handle .ps1 script options
$forwardArgs = @()
$env:DEV_MODE = "0"

foreach ($arg in $args) {
    if ($arg -eq "--use-new-frontend") {
        # Write-Host "[.ps1] Captured '--use-new-frontend' command"
        
    } elseif ($arg -eq "--dev") {
        Write-Host "[.ps1] Captured '--dev' command"
        $env:DEV_MODE = "1"
    } else {
        $forwardArgs += $arg
    }
}

# Start uvicorn
Write-Host "[.ps1] Starting uvicorn on port $BACKEND_PORT and extra args: '$forwardArgs'"
& .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --workers 1 --port $BACKEND_PORT @forwardArgs
