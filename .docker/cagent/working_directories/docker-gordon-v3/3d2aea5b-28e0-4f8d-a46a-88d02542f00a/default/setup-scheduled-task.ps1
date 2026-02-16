# Setup Windows Scheduled Task for Docker Security Monitor
# Run this script as Administrator

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Docker Security Monitor Setup" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MonitorScript = Join-Path $ScriptDir "docker-security-monitor.ps1"

# Verify monitor script exists
if (-not (Test-Path $MonitorScript)) {
    Write-Host "Error: docker-security-monitor.ps1 not found!" -ForegroundColor Red
    Write-Host "Please ensure both scripts are in the same directory." -ForegroundColor Red
    exit 1
}

# Task configuration
$TaskName = "DockerSecurityMonitor"
$TaskDescription = "Weekly Docker Scout security vulnerability scan"

# Remove existing task if it exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removing existing scheduled task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create task action
$Action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$MonitorScript`"" `
    -WorkingDirectory $ScriptDir

# Create task trigger (weekly on Monday at 9:00 AM)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Create task principal (run with highest privileges)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Register the scheduled task
Write-Host "Creating scheduled task: $TaskName" -ForegroundColor Green
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $TaskDescription `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal | Out-Null

Write-Host ""
Write-Host "==================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green
Write-Host ""
Write-Host "Task Details:" -ForegroundColor Cyan
Write-Host "  Name: $TaskName" -ForegroundColor White
Write-Host "  Schedule: Every Monday at 9:00 AM" -ForegroundColor White
Write-Host "  Script: $MonitorScript" -ForegroundColor White
Write-Host "  Logs: $ScriptDir\security-logs\" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Test the task: Run-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
Write-Host "  2. View logs in: $ScriptDir\security-logs\" -ForegroundColor White
Write-Host "  3. Modify schedule: taskschd.msc (search for '$TaskName')" -ForegroundColor White
Write-Host ""
Write-Host "To test now, run:" -ForegroundColor Cyan
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Green
Write-Host ""
