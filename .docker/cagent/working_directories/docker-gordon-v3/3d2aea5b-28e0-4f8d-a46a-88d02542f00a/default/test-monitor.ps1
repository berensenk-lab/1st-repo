# Test the Docker Security Monitor script manually
# This is useful for testing before setting up the scheduled task

Write-Host "Testing Docker Security Monitor..." -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MonitorScript = Join-Path $ScriptDir "docker-security-monitor.ps1"

if (-not (Test-Path $MonitorScript)) {
    Write-Host "Error: docker-security-monitor.ps1 not found!" -ForegroundColor Red
    exit 1
}

# Run the monitor script
& $MonitorScript

Write-Host ""
Write-Host "Test complete! Check the security-logs folder for results." -ForegroundColor Green
