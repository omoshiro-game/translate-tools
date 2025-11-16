#!/usr/bin/env pwsh
# Requires: PowerShell 5+ and internet access
$ErrorActionPreference = 'Stop'

# --- Config ---
$PyVer      = '3.8.10'
$Arch       = 'win32'  # 'amd64' for 64-bit
$BaseUrl    = "https://www.python.org/ftp/python/$PyVer"
$ZipName    = "python-$PyVer-embed-$Arch.zip"
$ZipUrl     = "$BaseUrl/$ZipName"

$Root       = (Get-Location).Path
$PyDir      = Join-Path $Root 'python'
$PythonExe  = Join-Path $PyDir 'python.exe'
$GetPipUrl  = 'https://bootstrap.pypa.io/pip/3.8/get-pip.py'  # Python 3.8–specific bootstrapper
$GetPip     = Join-Path $PyDir 'get-pip.py'


Write-Host "==> Creating portable Python in $PyDir"

# --- Prep dirs ---
New-Item -Type Directory -Force -Path $PyDir | Out-Null

# --- Download embeddable ZIP ---
$zipPath = Join-Path $Root $ZipName
if (-not (Test-Path $zipPath)) {
  Write-Host "==> Downloading $ZipUrl"
  Invoke-WebRequest -Uri $ZipUrl -OutFile $zipPath
} else {
  Write-Host "==> Using existing $zipPath"
}

# --- Extract ZIP ---
Write-Host "==> Extracting $ZipName"
Expand-Archive -Path $zipPath -DestinationPath $PyDir -Force

# --- Ensure Lib and site-packages exist ---
$LibDir = Join-Path $PyDir 'Lib'
$SitePk = Join-Path $LibDir 'site-packages'
New-Item -Type Directory -Force -Path $LibDir, $SitePk | Out-Null

# --- Enable site + add search paths in python38._pth ---
$pth = Get-ChildItem -Path $PyDir -Filter 'python38._pth' | Select-Object -First 1
if (-not $pth) {
  throw "Could not find python38._pth in $PyDir"
}
$pthPath = $pth.FullName

# Read existing lines as an array (one line per element)
$pthLines = @()
if (Test-Path $pthPath) {
    $pthLines = Get-Content -Path $pthPath -Encoding UTF8
}

# Ensure these entries exist (order not enforced; we just add missing ones)
$need = @(
    'python38.zip',
    '.\Lib',
    '.\Lib\site-packages',
    'import site'
)

foreach ($line in $need) {
    if ($pthLines -notcontains $line) {
        Add-Content -Path $pthPath -Encoding UTF8 -Value $line
    }
}
Write-Host "==> Patched $(Split-Path -Leaf $pthPath) for site + paths" -ForegroundColor Green

# --- Bootstrap pip (3.8-compatible script) ---
Write-Host "==> Downloading get-pip.py for Python 3.8"
Invoke-WebRequest -Uri $GetPipUrl -OutFile $GetPip

Write-Host "==> Installing pip with embedded Python"
& $PythonExe $GetPip

# --- Upgrade pip (optional but recommended) ---
Write-Host "==> Upgrading pip"
& $PythonExe -m pip install --upgrade pip

# --- Install tools into local site-packages ---
Write-Host "==> Installing frida and frida-tools"
& $PythonExe -m pip install --no-warn-script-location -r tools\requirements.txt

# --- Fetch agent.js and main.py ---
function Download-With-Fallback($primary, $fallback, $dest) {
  try {
    Invoke-WebRequest -Uri $primary -OutFile $dest -UseBasicParsing
  } catch {
    Write-Warning "Primary failed for $dest, trying fallback..."
    Invoke-WebRequest -Uri $fallback -OutFile $dest -UseBasicParsing
  }
}

# --- Create run.bat (uses embedded Python) ---
$RunBat = @"
@echo off
pushd "%~dp0"
python\python.exe "%~dp0\upgrade_all.py"
popd
"@
Set-Content -Path (Join-Path $Root 'upgrade_all.bat') -Value $RunBat -Encoding ASCII

Write-Host ""
Write-Host "==> Done."
Write-Host "Portable Python dir: $PyDir"
Write-Host "Upgrade to lastest engine:   .\upgrade_all.bat"
Write-Host ""