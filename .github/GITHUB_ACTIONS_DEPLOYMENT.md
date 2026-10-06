# GitHub Actions Automated Deployment Guide

**Status**: ✅ **AUTOMATED DEPLOYMENT READY**

This guide explains how the SG Property Bot automatically deploys to Fly.io using GitHub Actions whenever you push code changes.

## How It Works

### Trigger Events
The GitHub Actions workflow (`deploy-flyio.yml`) automatically runs on:
1. **Push to `main` or `master` branch** - Any code commit triggers deployment
2. **Manual dispatch** - You can manually trigger deployment from GitHub UI

### Deployment Pipeline

```
Push Code → Validate → Build & Deploy → Verify → Notify
   ↓          ↓           ↓              ↓        ↓
GitHub    Check Files  Fly.io         Tests    Telegram
   →        & Secrets    Deploy       Health    Alert
```

### Stage-by-Stage Breakdown

#### 1. **Validation Stage** (Runs on Ubuntu)
- ✅ Validates Python syntax for all core files
- ✅ Verifies required files exist (database_persistence.py, orchestrator_v3.py, etc.)
- ✅ Scans for hardcoded secrets
- **Status**: Must pass before proceeding

#### 2. **Build & Deploy Stage** (Runs on Ubuntu)
- ✅ Checks out code from GitHub
- ✅ Sets up Flyctl (Fly.io CLI tool)
- ✅ Deploys to Fly.io using `flyctl deploy`
- ✅ Uses `FLY_API_TOKEN` secret for authentication
- **Deployment Strategy**: `immediate` (no gradual rollout)
- **HA Mode**: Disabled (`--ha=false`) to reduce costs

#### 3. **Verification Stage** (Automated Checks)
- ✅ Checks deployment status on Fly.io
- ✅ Verifies database connectivity (if available)
- ⚠️ Continues even if DB check fails (graceful degradation)

#### 4. **Schedule Daily Job** (Optional)
- ✅ Configures scheduled machine for daily 06:00 AM SGT execution
- ✅ Sets environment variables for database connection
- ⚠️ Continues on error (may require manual setup)

#### 5. **Notifications**
- ✅ **On Success**: Telegram message confirming deployment
- ✅ **On Failure**: Telegram alert with GitHub Actions link

## GitHub Secrets Configuration

The workflow requires these secrets to be configured in GitHub repository settings:

### Required Secrets

| Secret Name | Description | Example | Where to Get |
|-------------|-------------|---------|--------------|
| `FLY_API_TOKEN` | Fly.io API token for authentication | `fm2_lJPECAA...` | Fly.io account settings |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications | `8864201770:AAAA...` | BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for notifications | `6834628591` | Your Telegram chat ID |

### Optional Secrets (used at deployment time)

These are injected into running containers on Fly.io:

| Secret Name | Purpose | Example |
|-------------|---------|---------|
| `DB_PASSWORD` | PostgreSQL database password | `secure_password_here` |
| `PROPERTYGURU_API_KEY` | PropertyGuru API key (if needed) | `api_key_here` |

### How to Add Secrets to GitHub

1. **Go to**: `GitHub Repository → Settings → Secrets and variables → Actions`
2. **Click**: "New repository secret"
3. **Add**:
   - Name: `FLY_API_TOKEN`
   - Value: Your Fly.io token (from `flyctl auth token`)
4. **Repeat** for each secret above
5. **Save**

### Retrieving Your Fly.io Token

```bash
flyctl auth login
# Opens browser for login
# Then run:
flyctl auth token
# Copy the output token
```

## Testing the Workflow

### Automatic Test (Push to Main)
```bash
git add .
git commit -m "test: trigger deployment workflow"
git push origin main
# GitHub Actions automatically starts
# Monitor at: GitHub → Actions tab
```

### Manual Test (GitHub UI)
1. Go to: `GitHub Repository → Actions`
2. Select: `Deploy SG Property Bot to Fly.io` workflow
3. Click: "Run workflow"
4. Choose branch (e.g., `main`)
5. Click: "Run workflow"
6. Watch progress in real-time

### View Deployment Logs

1. **GitHub Actions Logs**:
   - `GitHub → Actions → Latest Run → Click job → Expand steps`
   - Shows all validation, build, and deployment output

2. **Fly.io App Logs**:
   ```bash
   flyctl logs --app sg-property-bot --follow
   ```

3. **Fly.io Machine Status**:
   ```bash
   flyctl status --app sg-property-bot
   ```

## Troubleshooting

### Issue: Validation fails - "Missing file X"
**Solution**: Ensure all required Python files are in repo root:
- `database_persistence.py`
- `property_analytics.py`
- `orchestrator_v3.py`
- `fly.toml`
- `Dockerfile`

### Issue: "FLY_API_TOKEN not found"
**Solution**: Check GitHub Secrets:
```bash
# In GitHub UI:
# Settings → Secrets → Verify FLY_API_TOKEN exists
# If missing, add it with: flyctl auth token
```

### Issue: Deployment fails with "auth required"
**Solution**: Verify Fly.io token is valid:
```bash
flyctl auth token
# Token should be long alphanumeric string starting with "fm2_"
```

### Issue: Database connection fails during deployment
**Solution**: Expected if Fly.io PostgreSQL not yet created
- Workflow continues gracefully (doesn't fail deployment)
- Create database cluster manually:
  ```bash
  flyctl postgres create --app sg-property-bot-db
  ```

### Issue: Telegram notification not sent
**Solution**: Check GitHub Secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`
- Test locally: `curl -X POST "https://api.telegram.org/bot<TOKEN>/sendMessage" ...`

## Workflow File Location

The GitHub Actions workflow is stored at:
```
.github/workflows/deploy-flyio.yml
```

### Workflow Structure
```yaml
name: Deploy SG Property Bot to Fly.io
on:
  push:          # Triggers on code push
  workflow_dispatch:  # Manual trigger from GitHub UI
jobs:
  validate:      # Python syntax & file checks
  build-and-deploy:  # Fly.io deployment
  schedule-daily-job:  # Daily execution config
  notify-success:  # Success Telegram alert
  notify-failure:  # Failure Telegram alert
```

## Deployment Timeline

### For a typical deployment:
- **Validation**: 30-45 seconds
- **Build & Deploy**: 2-5 minutes (depends on Docker build)
- **Verification**: 15-30 seconds
- **Total**: ~3-7 minutes

### Daily Execution Schedule
- **Time**: 06:00 AM Singapore Time (SGT)
- **Cron**: `0 22 * * *` (UTC equivalent)
- **Frequency**: Once per day
- **Triggers**: Automated via Fly.io scheduled machine

## Monitoring Deployments

### GitHub Actions Dashboard
- **URL**: `https://github.com/ashfireball81/GeneralBot/actions`
- **Filter**: Search for "Deploy SG Property Bot" workflow
- **Status**: Shows ✅ (success), ❌ (failed), 🟡 (running)

### Fly.io Dashboard
- **URL**: `https://fly.io/apps/sg-property-bot`
- **Status**: See real-time app health, machines, logs
- **Metrics**: CPU, memory, and network usage

### Telegram Notifications
- Success: `✅ SG Property Bot successfully deployed to Fly.io`
- Failure: `❌ SG Property Bot deployment FAILED`

## Advanced: Customizing the Workflow

### Change deployment trigger
Edit `.github/workflows/deploy-flyio.yml`:
```yaml
on:
  push:
    branches:
      - main          # Change to 'dev' to deploy only on dev branch
      - production    # Add multiple branches
```

### Change deployment region
Edit `fly.toml`:
```toml
primary_region = "sin"  # Change to "syd" (Sydney), "fra" (Frankfurt), etc.
```

### Add pre-deployment tests
Edit `.github/workflows/deploy-flyio.yml`, add to `validate` job:
```yaml
- name: Run Python tests
  run: python -m pytest tests/
```

### Disable Telegram notifications
Edit `.github/workflows/deploy-flyio.yml`, comment out:
```yaml
# - name: Send Telegram notification
#   run: |
```

## Next Steps

1. ✅ **Workflow created**: `.github/workflows/deploy-flyio.yml`
2. ⏭️ **Add GitHub Secrets**:
   ```bash
   # From your laptop:
   flyctl auth token  # Copy this
   # Add to GitHub: Settings → Secrets → FLY_API_TOKEN
   ```
3. ⏭️ **Test deployment**:
   ```bash
   git add .
   git commit -m "feat: add github actions deployment workflow"
   git push origin main
   # Watch GitHub Actions tab
   ```
4. ⏭️ **Verify on Fly.io**:
   ```bash
   flyctl status --app sg-property-bot
   flyctl logs --app sg-property-bot --follow
   ```

## Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Auto-deployment on push | ✅ Ready | Triggers when code pushed to main |
| Pre-deployment validation | ✅ Ready | Checks syntax, files, secrets |
| Fly.io deployment | ✅ Ready | Uses `flyctl deploy` with remote builder |
| Health checks | ✅ Ready | Verifies deployment success |
| Database connection check | ⚠️ Optional | Graceful degradation if DB not ready |
| Telegram notifications | ✅ Ready | Alerts on success/failure |
| Daily scheduled execution | ⏭️ Setup | Requires `FLY_API_TOKEN` in GitHub |
| Cost optimization | ✅ Ready | Shared CPU (0.25x), 512MB RAM, auto-scale off |

---

**Status**: ✅ All components ready for automatic deployment via GitHub Actions!

**Last Updated**: 2026-10-06  
**Workflow Version**: 1.0  
**Compatibility**: GitHub Actions, Fly.io, Python 3.11+
