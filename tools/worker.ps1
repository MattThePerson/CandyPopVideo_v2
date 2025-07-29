$ErrorActionPreference = "Stop"

# Navigate to project root
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

# Run worker
& .\.venv\Scripts\python.exe -m python_src.worker $args
