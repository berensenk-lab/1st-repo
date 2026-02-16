# GitHub Actions - Docker Scout Security Scanning

Automated Docker security scanning workflows for CI/CD.

## Workflows

### 1. `docker-scout-cves.yml` - Scan Existing Images

Scans your published Docker images for CVEs on every push, PR, and weekly schedule.

**Triggers:**

- Push to main/master
- Pull requests to main/master
- Every Monday at 9:00 AM UTC
- Manual trigger via workflow_dispatch

**What it does:**

- Scans 5 configured images in parallel
- Generates SARIF reports
- Uploads results to GitHub Security tab
- Shows vulnerability summary in workflow

### 2. `docker-build-and-scan.yml` - Build & Scan on Changes

Builds and scans Docker images when Dockerfiles change.

**Triggers:**

- Push to main/master (when Dockerfiles change)
- Pull requests (when Dockerfiles change)
- Manual trigger

**What it does:**

- Finds all Dockerfiles in repo
- Builds each image
- Scans with Docker Scout
- Comments results on PRs

## Setup Instructions

### Step 1: Add Docker Hub Credentials (Optional)

For private images or to avoid rate limits:

1. Go to your repo: **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `DOCKER_SCOUT_HUB_USER` - Your Docker Hub username
   - `DOCKER_SCOUT_HUB_PASSWORD` - Docker Hub token or password

### Step 2: Enable Security Tab

1. Go to **Settings** → **Code security and analysis**
2. Enable **Dependency graph**
3. Enable **Dependabot alerts**
4. The SARIF uploads will appear under **Security** → **Code scanning**

### Step 3: Customize Image List

Edit `.github/workflows/docker-scout-cves.yml`:

```yaml
strategy:
  matrix:
    image:
      - your-org/your-image:tag
      - another-image:latest
```

Replace with your actual image names.

### Step 4: Commit and Push

```bash
git add .github/
git commit -m "Add Docker Scout CI/CD workflows

Assisted-By: cagent"
git push
```

## Viewing Results

### Workflow Logs

**Actions** tab → Select workflow run → View logs

### Security Alerts

**Security** tab → **Code scanning** → Filter by "docker-scout"

### PR Comments

Automatic comments on pull requests with scan summaries

## Workflow Files

| File | Purpose | Frequency |
|------|---------|-----------|
| `docker-scout-cves.yml` | Scan published images | Push, PR, Weekly |
| `docker-build-and-scan.yml` | Build & scan on changes | Dockerfile changes |

## Troubleshooting

### "Image not found"

- Ensure images exist and are accessible
- Check Docker Hub credentials are set
- For private images, add login secrets

### "Rate limit exceeded"

- Add `DOCKER_SCOUT_HUB_USER` and `DOCKER_SCOUT_HUB_PASSWORD` secrets
- Use authenticated requests to avoid rate limits

### "Permission denied"

- Ensure repository has Actions enabled
- Check workflow permissions in Settings → Actions → General

## Best Practices

1. **Keep image list updated** - Remove old images from the matrix
2. **Monitor Security tab regularly** - Review findings weekly
3. **Fix HIGH/CRITICAL first** - Prioritize severe vulnerabilities
4. **Update base images** - Keep base images current
5. **Use specific tags** - Avoid `latest` for reproducible scans

## Advanced Configuration

### Scan Only on Schedule

Remove `push` and `pull_request` triggers, keep only `schedule`.

### Scan Specific Branches

```yaml
on:
  push:
    branches: [ main, develop, 'release/*' ]
```

### Add Slack Notifications

Add a step to send results to Slack:

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
```

## Next Steps

- Set up scheduled task for local scanning (already done ✅)
- Configure branch protection rules requiring scan pass
- Integrate with your deployment pipeline
- Consider migrating to Docker Hardened Images (DHI)
