# Runs the go backend
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


# Build and run go backend
Write-Host "[.ps1] Building go"
go mod tidy -C go_backend
go build -C go_backend -ldflags="-s -w" -o "..\bin\$EXE_NAME.exe"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[.ps1] ERROR: Build exited with non-zero status $LASTEXITCODE"
    exit 1
}

# Run go
Write-Host "[.ps1] Starting $EXE_NAME.exe on port $BACKEND_PORT and extra args: '$args'"
& .\bin\$EXE_NAME.exe $args
