$ErrorActionPreference = "Stop"
Write-Host "Setting up Aurelia Boutique Enterprise..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\..\backend"
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Set-Location "..\frontend"
npm install
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Setup complete. Start backend and frontend using the scripts folder." -ForegroundColor Green
