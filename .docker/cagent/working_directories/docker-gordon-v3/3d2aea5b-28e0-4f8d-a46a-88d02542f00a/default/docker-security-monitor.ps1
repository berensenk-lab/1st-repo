# Docker Security Monitor - Weekly Scan
# This script runs Docker Scout CVE scanning and logs results

$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogDir = Join-Path $ScriptDir "security-logs"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$LogFile = Join-Path $LogDir "scan_$Timestamp.log"

# Create logs directory if it doesn't exist
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Start logging
Start-Transcript -Path $LogFile -Append

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Docker Security Monitor" -ForegroundColor Cyan
Write-Host "Scan started: $(Get-Date)" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Get all running containers
Write-Host "Scanning running containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Docker daemon not running or not accessible" -ForegroundColor Red
    Stop-Transcript
    exit 1
}

if ([string]::IsNullOrWhiteSpace($containers)) {
    Write-Host "No running containers found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Scanning local images instead..." -ForegroundColor Yellow
    $images = docker images --format "{{.Repository}}:{{.Tag}}" | Select-Object -First 5

    foreach ($image in $images) {
        if ($image -and $image -ne "<none>:<none>") {
            Write-Host ""
            Write-Host "Scanning image: $image" -ForegroundColor Green
            Write-Host "-----------------------------------" -ForegroundColor Gray
            docker scout cves $image
        }
    }
} else {
    # Scan each running container
    foreach ($container in $containers) {
        if ($container) {
            Write-Host ""
            Write-Host "Scanning container: $container" -ForegroundColor Green
            Write-Host "-----------------------------------" -ForegroundColor Gray
            docker scout cves $container
        }
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Scan completed: $(Get-Date)" -ForegroundColor Cyan
Write-Host "Log saved: $LogFile" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

Stop-Transcript

# Keep last 30 days of logs only
Get-ChildItem $LogDir -Filter "scan_*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force
