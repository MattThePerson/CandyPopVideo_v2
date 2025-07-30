# Runs the python backend (fastApi)
$ErrorActionPreference = "Stop"

# Set backend port
$BACKEND_PORT = 8000
$EXE_NAME = "CandyPopVideo"

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..


# Install venv
if (-Not (Test-Path ".venv\Scripts\activate.ps1")) {
    Write-Host "[.ps1] No python environment, please run make install"
    exit 1
}


# Start uvicorn
Write-Host "[.ps1] Starting uvicorn on port $BACKEND_PORT and extra args: '$args'"
go mod tidy -C go_backend
go build -C go_backend -ldflags="-s -w" -o "../$EXE_NAME.exe"
./CandyPopVideo.exe $args
