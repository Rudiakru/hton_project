# One-command demo runner (Windows PowerShell)
# - Builds demo pack
# - Verifies integrity (offline)
# - Starts backend and frontend demo servers
# - Prints the URL to open

$ErrorActionPreference = "Stop"

function Get-TsMs { return [int64]([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()) }

$root = (Resolve-Path (Join-Path $PSScriptRoot ".."))
$packTar = Join-Path $root "artifacts\demo_pack.tar.gz"
$packDir = Join-Path $root "artifacts\demo_pack"

# Detect Python
$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (Test-Path $venvPy) {
    Write-Host "Using venv python: $venvPy" -ForegroundColor Gray
    $pythonExe = $venvPy
} else {
    Write-Host "Using system python" -ForegroundColor Gray
    $pythonExe = (Get-Command python).Source
}

Write-Host "[1/5] Build demo matches + pack" -ForegroundColor Cyan
Push-Location $root
try {
  & $pythonExe scripts\generate_demo_matches.py --frames 120
  & $pythonExe scripts\build_demo_pack.py
} finally { Pop-Location }

Write-Host "[2/5] Extract pack" -ForegroundColor Cyan
if (Test-Path $packDir) { Remove-Item -Recurse -Force $packDir }
& tar -xzf $packTar -C (Join-Path $root "artifacts")

Write-Host "[3/5] Offline integrity verifier" -ForegroundColor Cyan
Push-Location $root
try {
  & $pythonExe (Join-Path $packDir "verify_integrity.py") --pack-root $packDir
} finally { Pop-Location }

Write-Host "[4/5] Start backend (http://127.0.0.1:8000)" -ForegroundColor Cyan
$env:DEMO_PACK_ROOT = $packDir
# $pythonExe is already set
$backend = Start-Process -FilePath $pythonExe -ArgumentList @("-m","uvicorn","backend.main:app","--host","127.0.0.1","--port","8000") -WorkingDirectory $root -PassThru

Write-Host "[5/5] Start frontend (http://127.0.0.1:5173)" -ForegroundColor Cyan
$env:REACT_APP_DEMO_MODE = "true"
$env:VITE_DEMO_MODE = "true"
$nodeExe = (Get-Command node).Source
$frontend = Start-Process -FilePath $nodeExe -ArgumentList @("node_modules\\vite\\bin\\vite.js","preview","--host","127.0.0.1","--port","5173","--strictPort") -WorkingDirectory (Join-Path $root "frontend") -PassThru

Start-Sleep -Seconds 2

Write-Host "Demo is ready." -ForegroundColor Green
Write-Host "Open: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host ("Backend PID: {0}, Frontend PID: {1}" -f $backend.Id, $frontend.Id)
Write-Host "Stop with: Stop-Process -Id <PID>"