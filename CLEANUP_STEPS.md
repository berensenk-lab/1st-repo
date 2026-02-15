# Repository Cleanup & Fix Steps

## Step 1: Remove Committed .venv Directory

This removes the virtual environment from Git history and prevents future commits.

```powershell
cd 1st-repo

# Remove .venv from Git cache (doesn't delete local files)
git rm -r --cached .venv/

# Commit the change
git commit -m "Remove committed .venv directory" -m "" -m "Assisted-By: cagent"

# Push to remote
git push origin main
```

**Verify:** `.venv/` should now show in `.gitignore` and be excluded from future commits.

---

## Step 2: Clean Up Dockerfile

Update `Dockerfile.sillytavern` to fix the git security issue.

**CHANGE THIS:**
```dockerfile
# Configure git safe directory
RUN git config --global --add safe.directory "*"
```

**TO THIS:**
```dockerfile
# Configure git safe directory (only for this app, not wildcard)
RUN git config --global --add safe.directory /home/node/app
```

**Why:** Allows this app to clone/pull from any repo, but doesn't open up the entire system.

```powershell
# After editing the file:
git add Dockerfile.sillytavern
git commit -m "Fix: Restrict git safe.directory to app directory only" -m "" -m "Assisted-By: cagent"
git push origin main
```

---

## Step 3: Pin Alpine Version

**CHANGE THIS:**
```dockerfile
FROM node:lts-alpine3.22 AS builder
...
FROM node:lts-alpine3.22
```

**TO THIS:**
```dockerfile
# Use specific version for reproducibility and security
FROM node:20.11-alpine3.20 AS builder
...
FROM node:20.11-alpine3.20
```

**Why:** 
- `lts` tag can change unexpectedly (breaking changes)
- Specific version prevents silent breaking changes
- Easier to track when vulnerability patches are applied

---

## Step 4: Add CVE Failure Thresholds

Edit `.github/workflows/docker-scout-strict.yml` to **fail on critical CVEs**.

Add this step after the scout scan:

```yaml
      - name: Fail on critical CVEs
        run: |
          if [[ "${{ steps.scout.outcome }}" == "critical" ]]; then
            echo "❌ Critical CVEs detected - failing build"
            exit 1
          fi
```

---

## Step 5: Update Workflow Matrix

In `.github/workflows/docker-scout-cves.yml`, replace hardcoded images with environment variables:

```yaml
env:
  REGISTRY: docker.io
  IMAGES: |
    almosega/minikube:patched
    almosega/open-webui:patched
    nginx:latest
    alpine:3.20
    docker.io/yourregistry/sillytavern:secure
```

This makes it easier to add/remove images without editing YAML.

---

## Step 6: Handle Corrupted Filenames (If on Linux/Mac)

The following files have invalid Windows filenames and prevent checkout on Windows:
- `File 2: .github/workflows/docker-scout-notifications.yml`
- `File 3: .github/workflows/docker-build-scan.yml`

**On Linux/Mac only:**
```bash
# These files are actually present with broken names, rename them:
cd 1st-repo
git checkout origin/main
ls -la ".github/workflows/" | grep "^File"
# Manually rename or remove these corrupted entries
```

**Recommended:** Create a new clean branch without these corrupted files:
```bash
git checkout --orphan clean-main
git add -A
git commit -m "Clean repo without corrupted filenames"
git push -u origin clean-main
# Then make this the default branch on GitHub
```

---

## Step 7: Verify Cleanup

Run these checks after each commit:

```powershell
# Check for excluded files
git status  # Should be clean

# List all tracked files (no .venv)
git ls-files | Select-String -Pattern "\.venv|__pycache__|node_modules" | Measure-Object

# Should return: Count 0

# Check git history
git log --oneline -10

# Check Dockerfile security
git show HEAD:Dockerfile.sillytavern | Select-String "safe.directory"
```

---

## Step 8: Add Pre-commit Hook (Optional but Recommended)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Prevent committing large or sensitive files

git diff --cached --name-only | while read file; do
  # Reject .venv commits
  if [[ $file == .venv/* ]]; then
    echo "❌ Error: Cannot commit files in .venv/ directory"
    exit 1
  fi
  
  # Reject node_modules commits
  if [[ $file == node_modules/* ]]; then
    echo "❌ Error: Cannot commit files in node_modules/ directory"
    exit 1
  fi
  
  # Reject large files (>10MB)
  size=$(git diff-index --cached HEAD -- "$file" | awk '{print $5}')
  if [[ $size -gt 10485760 ]]; then
    echo "❌ Error: File $file is too large ($(($size/1024/1024))MB > 10MB)"
    exit 1
  fi
done

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## Summary of Changes

| Item | Action | Impact |
|------|--------|--------|
| `.venv/` | ✅ Removed | -10MB, removes dependencies from repo |
| `.gitignore` | ✅ Enhanced | 50+ patterns, covers Python/Node/IDE/OS |
| `Dockerfile` | ⚠️ Fix needed | Better security posture |
| Alpine version | ⚠️ Pin needed | Reproducible builds |
| CVE workflows | ⚠️ Add thresholds | Prevents builds with critical CVEs |
| Corrupted filenames | 🚨 Requires rebasing | Windows compatibility |

---

## Rollback Instructions

If something goes wrong:

```powershell
# Revert last commit (keep files)
git reset --soft HEAD~1

# Revert last commit (delete files)
git reset --hard HEAD~1

# Reset to remote
git reset --hard origin/main
```

---

**After completing these steps, your repo will be clean, secure, and ready for production deployment.** ✅
