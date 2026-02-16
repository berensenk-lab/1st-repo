# Docker Security Monitor - Scheduled Task

Automated weekly Docker Scout vulnerability scanning for Windows.

## Quick Start

### 1. Test the Monitor First

```powershell
.\test-monitor.ps1
```

This runs a manual scan to verify everything works.

### 2. Set Up Weekly Scans

Run PowerShell **as Administrator**:

```powershell
.\setup-scheduled-task.ps1
```

This creates a scheduled task that runs every **Monday at 9:00 AM**.

### 3. Verify Setup

```powershell
# Check the task was created
Get-ScheduledTask -TaskName "DockerSecurityMonitor"

# Run a test scan immediately
Start-ScheduledTask -TaskName "DockerSecurityMonitor"

# Check the logs
Get-Content .\security-logs\scan_*.log -Tail 50
```

## What Gets Scanned

- **Running containers**: Scans all active Docker containers
- **Local images**: If no containers are running, scans your 5 most recent images
- **CVE detection**: Identifies security vulnerabilities with severity ratings
- **Trend tracking**: Logs saved for 30 days to track improvements

## Log Management

- **Location**: `.\security-logs\`
- **Format**: `scan_YYYY-MM-DD_HHmmss.log`
- **Retention**: Automatically deletes logs older than 30 days
- **Size**: Each log typically 5-50 KB depending on findings

## Customization

### Change Schedule

Open Task Scheduler (`taskschd.msc`) → Find "DockerSecurityMonitor" → Properties → Triggers

**Common schedules:**

- Daily: Change trigger to "Daily" at your preferred time
- Bi-weekly: Set to every 2 weeks
- After system startup: Add an "At startup" trigger

### Change What's Scanned

Edit `docker-security-monitor.ps1`:

- Line 36: Change `-First 5` to scan more/fewer images
- Add specific images: `docker scout cves your-image:tag`

### Notifications

Add to the end of `docker-security-monitor.ps1`:

```powershell
# Email notification (requires SMTP setup)
if ($criticalVulns -gt 0) {
    Send-MailMessage -To "you@example.com" -Subject "Critical vulnerabilities found"
}
```

## Troubleshooting

### Task doesn't run

```powershell
# Check task history
Get-ScheduledTask -TaskName "DockerSecurityMonitor" | Get-ScheduledTaskInfo

# View Task Scheduler logs
eventvwr.msc → Task Scheduler logs
```

### Docker not found

Ensure Docker Desktop is:

1. Installed and running
2. Added to system PATH
3. Accessible from PowerShell

### Permission errors

The task needs to run with elevated privileges. Ensure:

- Setup script was run as Administrator
- Task is configured to "Run with highest privileges"

## Manual Operations

### Run scan now

```powershell
.\docker-security-monitor.ps1
```

### Remove scheduled task

```powershell
Unregister-ScheduledTask -TaskName "DockerSecurityMonitor" -Confirm:$false
```

### View all logs

```powershell
Get-ChildItem .\security-logs\ | Sort-Object LastWriteTime -Descending
```

### Compare scans over time

```powershell
# View first and latest scan
$logs = Get-ChildItem .\security-logs\scan_*.log | Sort-Object Name
Get-Content $logs[0].FullName    # First scan
Get-Content $logs[-1].FullName   # Latest scan
```

## What's Next?

After running weekly scans for a few weeks, you'll have trend data showing:

- Security improvements after updates
- New vulnerabilities introduced
- Overall security posture over time

Consider setting up:

- GitHub Actions for CI/CD scanning
- Migration to Docker Hardened Images (DHI)
- Integration with security dashboards
