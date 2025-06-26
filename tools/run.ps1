$ErrorActionPreference = "Stop"

# Set backend port
$BACKEND_PORT = 8000

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

# Check if .venv exists
if (-Not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[VENV] No venv created, run tools\install.bat"
    exit 1
}

# [DEV] set env variable to determine frontend used

$useNew = $false
$forwardArgs = @()

foreach ($arg in $args) {
    if ($arg -eq "--use-new-frontend") {
        Write-Host "[DEV] Captured '--use-new-frontend' command"
        $useNew = $true
    } else {
        $forwardArgs += $arg
    }
}

if ($useNew) {
    Write-Host "[DEV] Using env variable to use NEW frontend"
    $env:USE_OLD_FRONTEND = "0"
} else {
    Write-Host "[DEV] Using env variable to use OLD frontend"
    $env:USE_OLD_FRONTEND = "1"
}

# Start uvicorn
Write-Host "[START] Starting uvicorn on port $BACKEND_PORT and extra args: '$forwardArgs'"
& .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --workers 1 --port $BACKEND_PORT @forwardArgs
