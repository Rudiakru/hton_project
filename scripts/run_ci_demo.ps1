$ErrorActionPreference = "Continue"

$root = (Resolve-Path (Join-Path $PSScriptRoot ".."))
$art = Join-Path $root "artifacts\ci_demo"

if (Test-Path $art) {
  Remove-Item -Recurse -Force $art
}
New-Item -ItemType Directory -Force $art | Out-Null

$backendLog = Join-Path $art "backend.log"
$backendErr = Join-Path $art "backend.stderr.log"
$frontendLog = Join-Path $art "frontend.log"
$frontendErr = Join-Path $art "frontend.stderr.log"
$pytestLog = Join-Path $art "pytest.log"
$summary = Join-Path $art "run_summary.md"
$integrityJson = Join-Path $art "integrity_report.json"

function Get-TsMs {
  return [int64]([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds())
}

function Wait-Http {
  param(
    [Parameter(Mandatory=$true)][string]$Url,
    [Parameter(Mandatory=$true)][int]$TimeoutSeconds
  )

  $t0 = Get-TsMs
  while ($true) {
    try {
      $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 1
      if ($r.StatusCode -eq 200) {
        return
      }
    } catch {
      # keep polling
    }

    $t1 = Get-TsMs
    $elapsed = [int](($t1 - $t0) / 1000)
    if ($elapsed -ge $TimeoutSeconds) {
      throw "Timed out waiting for $Url"
    }
    Start-Sleep -Milliseconds 200
  }
}

function Add-Summary {
  param([string]$Text)
  Add-Content -Path $summary -Value $Text
}

function Merge-LogStderr {
  param(
    [Parameter(Mandatory=$true)][string]$StdoutPath,
    [Parameter(Mandatory=$true)][string]$StderrPath
  )
  if (Test-Path $StderrPath) {
    try {
      Add-Content -Path $StdoutPath -Value "`n--- stderr ---" -ErrorAction SilentlyContinue
      Get-Content -Path $StderrPath -Encoding UTF8 -ErrorAction SilentlyContinue | Add-Content -Path $StdoutPath -ErrorAction SilentlyContinue
    } catch { }
    try { Remove-Item -Force $StderrPath } catch { }
  }
}

function Invoke-LoggedProcess {
  param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [Parameter(Mandatory=$true)][string[]]$ArgumentList,
    [Parameter(Mandatory=$true)][string]$WorkingDirectory,
    [Parameter(Mandatory=$true)][string]$StdoutPath,
    [Parameter(Mandatory=$true)][string]$StderrPath,
    [Parameter(Mandatory=$true)][string]$FailMessage
  )

  $p = Start-Process -FilePath $FilePath -ArgumentList $ArgumentList -WorkingDirectory $WorkingDirectory -NoNewWindow -Wait -PassThru -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
  Merge-LogStderr -StdoutPath $StdoutPath -StderrPath $StderrPath
  try { Get-Content -Path $StdoutPath -Encoding UTF8 -ErrorAction SilentlyContinue | Out-Host } catch { }
  if ($p.ExitCode -ne 0) { throw $FailMessage }
}

$backendProc = $null
$frontendProc = $null
$exitCode = 0
$startAll = Get-TsMs

$pythonExe = (Get-Command python).Source
$nodeExe = (Get-Command node).Source

# Prefer the .cmd shims to avoid PowerShell wrapper quirks when redirecting output
$npmExe = (Get-Command npm.cmd -ErrorAction SilentlyContinue).Source
if (-not $npmExe) { $npmExe = (Get-Command npm).Source }
$npxExe = (Get-Command npx.cmd -ErrorAction SilentlyContinue).Source
if (-not $npxExe) { $npxExe = (Get-Command npx).Source }

Set-Content -Path $summary -Value "# CI Demo Run Summary`n`n- Started: $([DateTimeOffset]::UtcNow.ToString('u'))"

try {
  $tDeps0 = Get-TsMs
  Add-Summary "`n## Install deps (python + node)"
  Push-Location $root
  try {
    (& python -m pip install -r requirements.txt 2>&1) | Tee-Object -FilePath (Join-Path $art "pip.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
  } finally {
    Pop-Location
  }

  Push-Location (Join-Path $root "frontend")
  try {
    (& $npmExe ci 2>&1) | Tee-Object -FilePath (Join-Path $art "npm_ci.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }

    (& $npxExe playwright install chromium 2>&1) | Tee-Object -FilePath (Join-Path $art "npm_ci.log") -Append | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "playwright install failed" }

    # Build once for deterministic and fast serving during E2E
    $env:REACT_APP_DEMO_MODE = "true"
    $env:VITE_DEMO_MODE = "true"
    # Use Start-Process redirection to avoid PowerShell emitting `NativeCommandError` records for non-fatal stderr output.
    Invoke-LoggedProcess `
      -FilePath $npmExe `
      -ArgumentList @("run", "build") `
      -WorkingDirectory (Join-Path $root "frontend") `
      -StdoutPath (Join-Path $art "frontend_build.log") `
      -StderrPath (Join-Path $art "frontend_build.stderr.log") `
      -FailMessage "frontend build failed"
  } finally {
    Pop-Location
  }

  $tDeps1 = Get-TsMs
  Add-Summary ("- duration_s: " + [math]::Round((($tDeps1 - $tDeps0) / 1000.0), 2))

  $tBuild0 = Get-TsMs
  Add-Summary "`n## Build demo matches + pack"
  Push-Location $root
  try {
    (& python scripts\generate_demo_matches.py --frames 120 2>&1) | Tee-Object -FilePath (Join-Path $art "build_matches.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "generate_demo_matches failed" }

    (& python scripts\build_demo_pack.py 2>&1) | Tee-Object -FilePath (Join-Path $art "build_pack.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "build_demo_pack failed" }

    # Determinism self-check: rebuild the pack and confirm the tarball hash matches.
    $packTar = Join-Path $root "artifacts\demo_pack.tar.gz"
    $sha1 = (Get-FileHash -Algorithm SHA256 -Path $packTar).Hash.ToLowerInvariant()
    (& python scripts\build_demo_pack.py 2>&1) | Tee-Object -FilePath (Join-Path $art "build_pack_2.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "build_demo_pack (second pass) failed" }
    $sha2 = (Get-FileHash -Algorithm SHA256 -Path $packTar).Hash.ToLowerInvariant()
    if ($sha1 -ne $sha2) {
      throw "demo_pack.tar.gz is not deterministic (sha1=$sha1, sha2=$sha2)"
    }
  } finally {
    Pop-Location
  }

  $tBuild1 = Get-TsMs
  $packTar = Join-Path $root "artifacts\demo_pack.tar.gz"
  $packSha = (Get-FileHash -Algorithm SHA256 -Path $packTar).Hash.ToLowerInvariant()
  Add-Summary ('- demo_pack.tar.gz sha256: `' + $packSha + '`')
  Add-Summary ("- duration_s: " + [math]::Round((($tBuild1 - $tBuild0) / 1000.0), 2))

  $tVerify0 = Get-TsMs
  Add-Summary "`n## Extract + offline integrity verifier"
  $packDir = Join-Path $root "artifacts\demo_pack"
  if (Test-Path $packDir) {
    Remove-Item -Recurse -Force $packDir
  }
  Push-Location $root
  try {
    (& tar -xzf $packTar -C (Join-Path $root "artifacts") 2>&1) | Tee-Object -FilePath (Join-Path $art "extract_pack.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "extract demo pack failed" }

    (& python (Join-Path $packDir "verify_integrity.py") --pack-root $packDir --out-json $integrityJson 2>&1) | Tee-Object -FilePath (Join-Path $art "offline_verify.log") | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "offline verify_integrity.py failed" }
  } finally {
    Pop-Location
  }

  $tVerify1 = Get-TsMs
  Add-Summary ("- duration_s: " + [math]::Round((($tVerify1 - $tVerify0) / 1000.0), 2))

  $tPy0 = Get-TsMs
  Add-Summary "`n## Run pytest"
  Push-Location $root
  try {
    (& pytest -q 2>&1) | Tee-Object -FilePath $pytestLog | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "pytest failed" }
  } finally {
    Pop-Location
  }

  $tPy1 = Get-TsMs
  Add-Summary ("- duration_s: " + [math]::Round((($tPy1 - $tPy0) / 1000.0), 2))

  $tServe0 = Get-TsMs
  Add-Summary "`n## Start backend + frontend (demo mode)"
  $env:DEMO_PACK_ROOT = $packDir

  $backendProc = Start-Process -FilePath $pythonExe -ArgumentList @(
    "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"
  ) -WorkingDirectory $root -NoNewWindow -PassThru -RedirectStandardOutput $backendLog -RedirectStandardError $backendErr

  Wait-Http -Url "http://127.0.0.1:8000/api/demo/health" -TimeoutSeconds 60

  $env:REACT_APP_DEMO_MODE = "true"
  # Avoid `npm.cmd`/`npm.ps1` shims (hard to run with redirected output); run Vite directly via Node.
  $frontendProc = Start-Process -FilePath $nodeExe -ArgumentList @(
    "node_modules\\vite\\bin\\vite.js",
    "preview",
    "--host",
    "127.0.0.1",
    "--port",
    "5173",
    "--strictPort"
  ) -WorkingDirectory (Join-Path $root "frontend") -NoNewWindow -PassThru -RedirectStandardOutput $frontendLog -RedirectStandardError $frontendErr

  Wait-Http -Url "http://127.0.0.1:5173/" -TimeoutSeconds 60

  $tE2E0 = Get-TsMs
  Add-Summary "`n## Playwright E2E (demo flow)"
  $pwOut = Join-Path $art "playwright"
  if (Test-Path $pwOut) { Remove-Item -Recurse -Force $pwOut }
  New-Item -ItemType Directory -Force $pwOut | Out-Null

  $env:PLAYWRIGHT_OUTPUT_DIR = $pwOut
  $env:E2E_BASE_URL = "http://127.0.0.1:5173"

  Push-Location (Join-Path $root "frontend")
  try {
    Invoke-LoggedProcess `
      -FilePath $npmExe `
      -ArgumentList @("run", "e2e:demo") `
      -WorkingDirectory (Join-Path $root "frontend") `
      -StdoutPath (Join-Path $art "e2e.log") `
      -StderrPath (Join-Path $art "e2e.stderr.log") `
      -FailMessage "playwright e2e failed"
    $e2eCode = 0
  } finally {
    Pop-Location
  }

  if ($e2eCode -ne 0) {
    $shots = Get-ChildItem -Path $pwOut -Recurse -File -Filter "*.png" -ErrorAction SilentlyContinue
    $i = 0
    foreach ($s in $shots) {
      Copy-Item -Force $s.FullName (Join-Path $art ("e2e_screenshot_{0}.png" -f $i))
      $i++
    }

    $vid = Get-ChildItem -Path $pwOut -Recurse -File -Filter "*.webm" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($vid) {
      Copy-Item -Force $vid.FullName (Join-Path $art "e2e_video.webm")
    }

    throw "playwright e2e failed"
  }

  $tE2E1 = Get-TsMs
  Add-Summary ("- duration_s: " + [math]::Round((($tE2E1 - $tE2E0) / 1000.0), 2))

  $tServe1 = Get-TsMs
  Add-Summary ("- services+e2e_total_s: " + [math]::Round((($tServe1 - $tServe0) / 1000.0), 2))

  $endAll = Get-TsMs
  $totalS = [int](($endAll - $startAll) / 1000)
  Add-Summary "`n### Status: PASS`n- Total time: ${totalS}s`n"

  Write-Host "CI demo run OK" -ForegroundColor Green
} catch {
  $exitCode = 1
  $errMsg = $_.Exception.Message
  if (-not $errMsg) {
    $errMsg = ($_ | Out-String)
  }
  Add-Summary "`n### Status: FAIL`n- Reason: $errMsg"
  Write-Host "CI demo run FAILED: $errMsg" -ForegroundColor Red
} finally {
  if ($frontendProc -and -not $frontendProc.HasExited) {
    try { Stop-Process -Id $frontendProc.Id -Force } catch { }
    try { Wait-Process -Id $frontendProc.Id -Timeout 10 -ErrorAction SilentlyContinue } catch { }
  }
  if ($backendProc -and -not $backendProc.HasExited) {
    try { Stop-Process -Id $backendProc.Id -Force } catch { }
    try { Wait-Process -Id $backendProc.Id -Timeout 10 -ErrorAction SilentlyContinue } catch { }
  }

  if (Test-Path $backendErr) {
    try {
      # Best-effort merge (ignore file locks during teardown)
      Add-Content -Path $backendLog -Value "`n--- stderr ---" -ErrorAction SilentlyContinue
      Get-Content -Path $backendErr -ErrorAction SilentlyContinue | Add-Content -Path $backendLog -ErrorAction SilentlyContinue
    } catch { }
    try { Remove-Item -Force $backendErr } catch { }
  }
  if (Test-Path $frontendErr) {
    try {
      Add-Content -Path $frontendLog -Value "`n--- stderr ---" -ErrorAction SilentlyContinue
      Get-Content -Path $frontendErr -ErrorAction SilentlyContinue | Add-Content -Path $frontendLog -ErrorAction SilentlyContinue
    } catch { }
    try { Remove-Item -Force $frontendErr } catch { }
  }
}

exit $exitCode
