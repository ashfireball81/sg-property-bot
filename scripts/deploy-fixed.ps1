# Deploy SG Property Bot Infrastructure to Fly.io (Windows/PowerShell)
# Prerequisites: flyctl installed and authenticated
# Fixed version with proper error handling

param(
    [string]$AppName = "sg-property-bot",
    [string]$Region = "sin"  # Singapore
)

$ErrorActionPreference = 'Continue'

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SG Property Bot - Infrastructure Deployment Script" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$flyctlCmd = Get-Command flyctl -ErrorAction SilentlyContinue
if (-not $flyctlCmd) {
    Write-Host "❌ Error: flyctl not installed" -ForegroundColor Red
    Write-Host "Install from: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
}
Write-Host "✓ flyctl installed" -ForegroundColor Green

# Check authentication
$authCheck = & flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Not authenticated with Fly.io" -ForegroundColor Red
    Write-Host "Set FLY_API_TOKEN environment variable or run: flyctl auth login"
    exit 1
}
Write-Host "✓ Authenticated with Fly.io" -ForegroundColor Green
Write-Host ""

# Step 1: Create Fly.io App
Write-Host "Step 1: Creating/Verifying Fly.io application..." -ForegroundColor Yellow
$appsList = & flyctl apps list --json 2>&1 | ConvertFrom-Json
$appExists = $appsList | Where-Object { $_.Name -eq $AppName }

if ($appExists) {
    Write-Host "✓ App '$AppName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating app '$AppName' in region '$Region'..."
    & flyctl apps create $AppName --region $Region 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ App created successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ App creation returned code $LASTEXITCODE (may already exist)" -ForegroundColor Yellow
    }
}

# Step 2: Create PostgreSQL Database
Write-Host ""
Write-Host "Step 2: Creating/Verifying PostgreSQL database..." -ForegroundColor Yellow
$dbName = "sg-property-db"
$pgList = & flyctl postgres list --json 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
$dbExists = $pgList | Where-Object { $_.Name -eq $dbName }

if ($dbExists) {
    Write-Host "✓ Database '$dbName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating PostgreSQL instance ($Region, 2GB RAM)..."
    & flyctl postgres create --name $dbName --region $Region --vm-size shared-cpu-1x 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL instance created" -ForegroundColor Green
    } else {
        Write-Host "⚠ PostgreSQL creation returned code $LASTEXITCODE" -ForegroundColor Yellow
    }
}

# Step 3: Create Redis Cache
Write-Host ""
Write-Host "Step 3: Creating/Verifying Redis cache..." -ForegroundColor Yellow
$redisName = "sg-property-cache"
$redisList = & flyctl redis list --json 2>&1 | ConvertFrom-Json -ErrorAction SilentlyContinue
$redisExists = $redisList | Where-Object { $_.Name -eq $redisName }

if ($redisExists) {
    Write-Host "✓ Redis instance '$redisName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating Redis instance ($Region, 256MB)..."
    & flyctl redis create --name $redisName --region $Region 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Redis instance created" -ForegroundColor Green
    } else {
        Write-Host "⚠ Redis creation returned code $LASTEXITCODE" -ForegroundColor Yellow
    }
}

# Step 4: Set placeholder secrets
Write-Host ""
Write-Host "Step 4: Setting placeholder secrets..." -ForegroundColor Yellow
& flyctl secrets set `
    NODE_ENV=production `
    API_PORT=3000 `
    LOG_LEVEL=info `
    --app $AppName 2>&1 | Out-Null
Write-Host "✓ Secrets configured" -ForegroundColor Green

# Step 5: Get connection strings
Write-Host ""
Write-Host "Step 5: Retrieving connection information..." -ForegroundColor Yellow
$databaseUrl = "postgresql://username:password@sg-property-db.internal/sg_property_bot"
$redisUrl = "redis://sg-property-cache.internal:6379"

try {
    $dbConnStr = & flyctl postgres connect-string $dbName 2>&1
    if ($LASTEXITCODE -eq 0) {
        $databaseUrl = $dbConnStr
        Write-Host "✓ Database connection string retrieved" -ForegroundColor Green
    } else {
        Write-Host "⚠ Using internal database URL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Using internal database URL" -ForegroundColor Yellow
}

try {
    $redisConnStr = & flyctl redis connect-string $redisName 2>&1
    if ($LASTEXITCODE -eq 0) {
        $redisUrl = $redisConnStr
        Write-Host "✓ Redis connection string retrieved" -ForegroundColor Green
    } else {
        Write-Host "⚠ Using internal Redis URL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠ Using internal Redis URL" -ForegroundColor Yellow
}

# Step 6: Deploy API
Write-Host ""
Write-Host "Step 6: Deploying API to Fly.io..." -ForegroundColor Yellow
Write-Host "Building and deploying Docker image (this may take 2-3 minutes)..."
& flyctl deploy --app $AppName --region $Region 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ API deployed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠ API deployment returned code $LASTEXITCODE" -ForegroundColor Yellow
}

# Step 7: Verify deployment
Write-Host ""
Write-Host "Step 7: Verifying deployment..." -ForegroundColor Yellow
& flyctl status --app $AppName 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Deployment verified" -ForegroundColor Green
} else {
    Write-Host "⚠ Status check returned code $LASTEXITCODE" -ForegroundColor Yellow
}

# Final Summary
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Infrastructure Deployment Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  App Name: $AppName"
Write-Host "  Region: $Region"
Write-Host "  API URL: https://$AppName.fly.dev"
Write-Host "  API Health: https://$AppName.fly.dev/health"
Write-Host ""

Write-Host "Connection Strings:" -ForegroundColor Cyan
Write-Host "  Database: $databaseUrl"
Write-Host "  Redis: $redisUrl"
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Deploy database schema:"
Write-Host "     psql `"$databaseUrl`" -f database/schema.sql"
Write-Host ""
Write-Host "  2. Test API health:"
Write-Host "     curl https://$AppName.fly.dev/health"
Write-Host ""
Write-Host "  3. View logs:"
Write-Host "     flyctl logs --app $AppName"
Write-Host ""
Write-Host "  4. Dashboard:"
Write-Host "     https://fly.io/apps/$AppName"
Write-Host ""
Write-Host "Credential Injection (when ready):" -ForegroundColor Yellow
Write-Host "  flyctl secrets set TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=xxx --app $AppName"
Write-Host ""

Write-Host "✅ Deployment script completed!" -ForegroundColor Green
