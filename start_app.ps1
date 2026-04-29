# Image-to-Video AI App - Robust Start Script for Windows

$RootPath = Get-Location
Write-Host "--- Starting Image-to-Video AI App Setup at $RootPath ---" -ForegroundColor Cyan

# 1. Setup Backend
Write-Host "`n[1/3] Setting up Backend..." -ForegroundColor Yellow
Push-Location "backend"
if (!(Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..."
    python -m venv venv
}
.\venv\Scripts\python -m pip install --upgrade pip
.\venv\Scripts\pip install -r requirements.txt

# Start Backend in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\backend'; .\venv\Scripts\activate; python main.py"
Write-Host "Check: Backend API window opened." -ForegroundColor Green

# Start Worker in a new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$RootPath\backend'; .\venv\Scripts\activate; python worker.py"
Write-Host "Check: Background Worker window opened." -ForegroundColor Green
Pop-Location

# 2. Setup Frontend
Write-Host "`n[2/3] Setting up Frontend..." -ForegroundColor Yellow

# Start Frontend setup and dev server in ONE window to ensure it finishes before starting
$FrontendCmd = @"
Set-Location '$RootPath\frontend'
if (Test-Path 'node_modules') {
    Write-Host 'Cleaning up node_modules...' -ForegroundColor Gray
    Remove-Item -Recurse -Force 'node_modules'
}
if (Test-Path 'package-lock.json') {
    Remove-Item -Force 'package-lock.json'
}
Write-Host 'Installing dependencies (this may take a minute)...' -ForegroundColor Yellow
npm install --legacy-peer-deps
Write-Host 'Starting dev server...' -ForegroundColor Green
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendCmd
Write-Host "Check: Frontend window opened (Installation in progress...)" -ForegroundColor Green

Write-Host "`n[3/3] ALL SYSTEMS STARTING!" -ForegroundColor Cyan
Write-Host "-------------------------------------------"
Write-Host "1. Look at the new Frontend window. It will install packages THEN start."
Write-Host "2. Once it shows a URL (like http://localhost:5173), open it."
Write-Host "3. Upload an image and enjoy!"
Write-Host "-------------------------------------------"
Write-Host "To stop everything, just close the three new PowerShell windows."
