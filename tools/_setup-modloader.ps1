#!/usr/bin/env pwsh
# _setup-modloader.ps1
# Sets up the Aquedi4 modloader in the current game directory.
# Requires: PowerShell 5+ and internet access
$ErrorActionPreference = 'Stop'

# Paths / config
$Root          = (Get-Location).Path
$GameExeName   = 'Game_v1020.exe'
$GameExePath   = Join-Path $Root $GameExeName

$RepoOwner     = 'omoshiro-game'
$RepoName      = 'aquedi4-modoader'   # repo name as given
$AssetName     = 'dist.zip'

# Fallback URL if latest-release lookup fails or has no dist.zip
$FallbackDistUrl = 'https://github.com/omoshiro-game/aquedi4-modoader/releases/download/0.0.1/dist.zip'

$DistZipName   = 'modloader-dist.zip'
$DistZipPath   = Join-Path $Root $DistZipName

$HookedDllName = 'd3d9Hooked.dll'
$HookedDllPath = Join-Path $Root $HookedDllName

# Ensure we are in the game root
if (-not (Test-Path $GameExePath)) {
    Write-Error "Game executable '$GameExeName' not found in '$Root'. Run this script in the game root folder."
    return
}

Write-Host "==> Game root detected: $Root"
Write-Host "==> Found $GameExeName"

# Determine download URL for dist.zip (latest release if possible)
$DistUrl = $FallbackDistUrl
$usedFallback = $true

try {
    Write-Host "==> Querying GitHub latest release for $RepoOwner/$RepoName"

    $apiUrl  = "https://api.github.com/repos/$RepoOwner/$RepoName/releases/latest"
    $headers = @{ 'User-Agent' = 'setup_modloader.ps1' }

    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers
    if ($null -ne $release -and $release.assets) {
        $asset = $release.assets | Where-Object { $_.name -eq $AssetName } | Select-Object -First 1
        if ($asset -and $asset.browser_download_url) {
            $DistUrl      = $asset.browser_download_url
            $usedFallback = $false
            Write-Host "==> Using latest release dist.zip from tag '$($release.tag_name)'"
        } else {
            Write-Warning "No '$AssetName' asset found in latest release. Falling back to $FallbackDistUrl"
        }
    } else {
        Write-Warning "Latest release info is empty or invalid. Falling back to $FallbackDistUrl"
    }
}
catch {
    Write-Warning "Failed to query GitHub latest release: $($_.Exception.Message)"
    Write-Warning "Falling back to $FallbackDistUrl"
}

if ($usedFallback) {
    Write-Host "==> dist.zip URL: $DistUrl (fallback)"
} else {
    Write-Host "==> dist.zip URL: $DistUrl"
}

# Download dist.zip into game root
Write-Host "==> Downloading modloader dist.zip..."
Invoke-WebRequest -Uri $DistUrl -OutFile $DistZipPath

# Extract dist.zip directly into the game root
Write-Host "==> Extracting dist.zip into game root"
Expand-Archive -Path $DistZipPath -DestinationPath $Root -Force

# Delete the ZIP afterwards:
Remove-Item -Path $DistZipPath -Force

# Create d3d9Hooked.dll from the system 32-bit d3d9.dll
Write-Host "==> Locating system 32-bit d3d9.dll to use as $HookedDllName"

# On 64-bit Windows, 32-bit DLLs live in SysWOW64; on 32-bit Windows, System32 is 32-bit.
$systemD3D9Path = $null
if ([Environment]::Is64BitOperatingSystem) {
    $systemD3D9Path = Join-Path $env:WINDIR 'SysWOW64\d3d9.dll'
} else {
    $systemD3D9Path = Join-Path $env:WINDIR 'System32\d3d9.dll'
}

if (-not (Test-Path $systemD3D9Path)) {
    Write-Warning "Could not find system 32-bit d3d9.dll at '$systemD3D9Path'."
    Write-Warning "d3d9Hooked.dll will NOT be created. You may need to copy it manually."
} else {
    Write-Host "==> Copying '$systemD3D9Path' to '$HookedDllPath'"
    Copy-Item -Path $systemD3D9Path -Destination $HookedDllPath -Force
    Write-Host "==> d3d9Hooked.dll created successfully."
}

Write-Host ""
Write-Host "==> Modloader setup complete."
Write-Host "    - Game root: $Root"
Write-Host "    - scripts folder should now be present."
Write-Host "    - d3d9.dll (proxy) should be in the game root."
Write-Host "    - $HookedDllName points to the system's original 32-bit d3d9.dll."
Write-Host ""
