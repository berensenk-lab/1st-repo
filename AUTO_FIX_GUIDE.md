# Auto-Fix Workflow Starter Kit

A complete CI/CD automation system that detects and automatically fixes code issues across your projects.

## What's Included

**Automated Detection For:**
- Code formatting issues (Black, isort)
- Linting problems (pylint, flake8)
- Security vulnerabilities (bandit, git-secrets)
- Outdated dependencies (pip, npm)
- Docker best practices
- Git commit quality

**Automated Fixes For:**
- Code formatting and import ordering
- Dependency updates
- Basic security improvements
- Configuration optimization

**Validation & Safety:**
- Runs tests after each fix
- Creates PRs for human review (not direct commits)
- Comprehensive validation chain
- Rollback-friendly (based on git)

## Quick Start

### 1. Copy Files to Your Repository

All files are already in place in your repo.

### 2. Update Your Requirements

Ensure your project has these Python dependencies for the agent:

```txt
# requirements-dev.txt (for CI environment)
pyyaml
requests
click
colorama
gitpython
bandit
pylint
black
isort
pytest
```

### 3. Enable in GitHub

- No additional setup needed - the workflow runs automatically
- Runs on: push to main/develop, daily schedule
- Creates PRs with fixes
- Requires review before merge (recommended)

### 4. Customize Configuration

Edit `.autofixer.yml` to:
- Enable/disable specific detectors
- Control which issues auto-fix vs require review
- Adjust validation rules
- Exclude paths or file types

## How It Works

### Workflow Execution Flow

```
┌─────────────────────────────────────────────────────┐
│ GitHub Actions Trigger                              │
│ (push, schedule, manual)                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Build Fixer Container                               │
│ (with all detection tools)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Issue Detection Phase                               │
│ • Formatting checks                                 │
│ • Linting scans                                     │
│ • Security scanning                                 │
│ • Dependency analysis                               │
│ • Config validation                                 │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Apply Fixes (Fixable Issues Only)                   │
│ • Auto-format code                                  │
│ • Sort imports                                      │
│ • Update dependencies                               │
│ • Optimize configs                                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Validation Phase                                    │
│ • Run unit tests                                    │
│ • Docker build check                                │
│ • docker-compose validate                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ Create PR if Changes Found                          │
│ • Descriptive title and body                        │
│ • Auto labels (automated, bot, fixes)               │
│ • Ready for human review and merge                  │
└─────────────────────────────────────────────────────┘
```

## Detected Issues & Fixes

| Category | Detection Tool | Auto-Fixable | Notes |
|----------|---|---|---|
| Formatting | Black | ✓ | Runs `black` on codebase |
| Import Ordering | isort | ✓ | Sorts Python imports |
| Linting | pylint | ~ | Detects, partial auto-fix |
| Security | bandit | ✗ | Detects, requires review |
| Dependencies | pip/npm | ✓ | Runs update commands |
| Docker | Custom | ~ | Suggests best practices |
| Git Commits | Custom | ✗ | Detects, requires review |

**Legend:** ✓ = Auto-fix | ~ = Partial | ✗ = Requires review

## Configuration Examples

### Disable Dependency Auto-Updates

```yaml
# .autofixer.yml
fixers:
  auto_dependencies: false  # Requires human review
```

### Run Only on Specific Branches

Edit `.github/workflows/auto-fix.yml`:
```yaml
on:
  push:
    branches: [main]  # Only main branch
```

### Disable Daily Schedule

Edit `.github/workflows/auto-fix.yml`:
```yaml
on:
  push:
    branches: [main, develop]
  # Remove the 'schedule' section
```

### Exclude Paths from Fixes

```yaml
# .autofixer.yml
exclude_paths:
  - vendor/
  - migrations/
  - generated/
```

## Advanced Usage

### Extending with Custom Detectors

Add to `scripts/detectors.py`:

```python
class CustomDetector:
    @staticmethod
    def detect_custom_issue(workspace: Path) -> DetectionResult:
        # Your detection logic
        return DetectionResult(
            category="custom",
            found=True,
            count=issues_found,
            details={...},
            severity="medium"
        )
```

### Extending with Custom Fixers

Add to `scripts/fixers.py`:

```python
class CustomFixer:
    @staticmethod
    def fix_custom_issue(workspace: Path) -> bool:
        # Your fix logic
        return True

# Register it
FixerRegistry.register("custom", CustomFixer)
```

### Local Testing

Run the agent locally:

```bash
# Build the fixer image
docker build -f Dockerfile.fixer -t fixer:latest .

# Run detection and fixes
docker run --rm -v $(pwd):/workspace -w /workspace fixer:latest \
  python /fixer/agent.py

# Check what changed
git diff
git status
```

## Best Practices

### 1. Start Conservative
- Enable only safe, auto-fixable issues first
- Let humans review all PRs before merging
- Gradually add more aggressive fixes

### 2. Monitor PR Creation
- Review the first few auto-fix PRs manually
- Ensure fixes match your project standards
- Adjust configuration as needed

### 3. Team Communication
- Let your team know the workflow is active
- Link to this documentation in PR descriptions
- Use labels to identify bot-created PRs

### 4. Customize for Your Project
- Add project-specific validators
- Exclude generated/vendor code
- Set severity levels appropriate to your needs

## Troubleshooting

### No PRs Created

**Check:**
1. GitHub Actions is enabled in repository settings
2. Workflow file is in `.github/workflows/auto-fix.yml`
3. Branch is `main` or `develop`
4. Runner has sufficient permissions

**Debug:**
```bash
# Check workflow run logs in GitHub Actions tab
# View what files changed
git status
git diff
```

### Validation Fails

**Check:**
1. Tests pass locally: `pytest` or `npm test`
2. Docker build works: `docker build .`
3. docker-compose valid: `docker compose config`

**Debug:**
```bash
# Run validation locally
docker run --rm -v $(pwd):/workspace \
  -f Dockerfile.test -t test:latest .
docker run --rm test:latest
```

### Container Build Fails

Check `Dockerfile.fixer`:
- All required tools installed
- Python packages included
- Script paths correct

Rebuild with:
```bash
docker build --no-cache -f Dockerfile.fixer -t fixer:latest .
```

## Security Considerations

⚠️ **Important:**

- **Read-Only by Default**: Issues detection only, review before applying fixes
- **PR-Based Safety**: Changes go to PRs, not direct commits
- **Access Control**: Ensure bot has proper GitHub token permissions
- **Secrets**: Don't store credentials in `.autofixer.yml`
- **Review Process**: Always review auto-fix PRs before merging

## Extending the System

### Add Support for More Languages

1. Create language-specific detector in `scripts/detectors.py`
2. Create language-specific fixer in `scripts/fixers.py`
3. Create language-specific validator in `scripts/validators.py`
4. Update `Dockerfile.fixer` with required tools
5. Update `.autofixer.yml` configuration

### Integrate with External Services

Modify `scripts/agent.py` to:
- Call external APIs for issue tracking
- Send notifications to Slack/Discord
- Report metrics to monitoring systems

## Performance Tuning

For large repositories:

```yaml
# .autofixer.yml
detection:
  # Disable expensive checks
  security: false
  linting: false

  # Run only periodically
  docker: false
```

Run expensive checks on a different schedule:
```bash
# Separate workflow for expensive checks
schedule:
  - cron: '0 0 * * 0'  # Weekly
```

## Support & Contributions

- Issues? Check the troubleshooting section
- Want to extend? Follow the architecture patterns
- Questions? Review the code comments

## License

This starter kit is provided as-is for use with Docker and your projects.

---

**Last Updated:** 2024
**Version:** 1.0
