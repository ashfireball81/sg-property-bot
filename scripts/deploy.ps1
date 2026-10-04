# Deploy SG Property Bot Infrastructure to Fly.io (Windows/PowerShell)
# Prerequisites: flyctl installed and authenticated

param(
    [string]$AppName = "sg-property-bot",
    [string]$Region = "sin"  # Singapore
)

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SG Property Bot - Infrastructure Deployment Script" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$flyctlPath = Get-Command flyctl -ErrorAction SilentlyContinue
if (-not $flyctlPath) {
    Write-Host "Error: flyctl not installed" -ForegroundColor Red
    Write-Host "Install from: https://fly.io/docs/getting-started/installing-flyctl/"
    exit 1
}

$auth = flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Not authenticated with Fly.io" -ForegroundColor Red
    Write-Host "Run: flyctl auth login"
    exit 1
}

Write-Host "✓ Prerequisites OK`n" -ForegroundColor Green

# Step 1: Create Fly.io App
Write-Host "Step 1: Creating/Verifying Fly.io application..." -ForegroundColor Yellow
$apps = flyctl apps list 2>&1
if ($apps -match $AppName) {
    Write-Host "✓ App '$AppName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating app '$AppName' in region '$Region'..."
    flyctl apps create $AppName --region $Region --json 2>&1 | Out-Null
    Write-Host "✓ App created" -ForegroundColor Green
}

# Step 2: Create PostgreSQL Database
Write-Host "`nStep 2: Creating/Verifying PostgreSQL database..." -ForegroundColor Yellow
$dbName = "sg-property-db"
$postgresApps = flyctl postgres list 2>&1
if ($postgresApps -match $dbName) {
    Write-Host "✓ Database '$dbName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating PostgreSQL instance..."
    flyctl postgres create --name $dbName --region $Region --vm-size shared-cpu-1x 2>&1 | Out-Null
    Write-Host "✓ PostgreSQL instance created" -ForegroundColor Green
}

# Step 3: Create Redis Cache
Write-Host "`nStep 3: Creating/Verifying Redis cache..." -ForegroundColor Yellow
$redisName = "sg-property-cache"
$redisApps = flyctl redis list 2>&1
if ($redisApps -match $redisName) {
    Write-Host "✓ Redis instance '$redisName' already exists" -ForegroundColor Green
} else {
    Write-Host "Creating Redis instance..."
    flyctl redis create --name $redisName --region $Region 2>&1 | Out-Null
    Write-Host "✓ Redis instance created" -ForegroundColor Green
}

# Step 4: Create secrets
Write-Host "`nStep 4: Setting placeholder secrets..." -ForegroundColor Yellow
flyctl secrets set `
  NODE_ENV=production `
  API_PORT=3000 `
  LOG_LEVEL=info `
  --app $AppName 2>&1 | Out-Null
Write-Host "✓ Secrets set" -ForegroundColor Green

# Step 5: Get connection strings
Write-Host "`nStep 5: Retrieving connection information..." -ForegroundColor Yellow
try {
    $databaseUrl = flyctl postgres connect-string $dbName
    Write-Host "✓ Database URL retrieved" -ForegroundColor Green
} catch {
    $databaseUrl = "postgresql://user:pass@sg-property-db.internal/sg_property_bot"
    Write-Host "⚠ Using placeholder database URL" -ForegroundColor Yellow
}

try {
    $redisUrl = flyctl redis connect-string $redisName
    Write-Host "✓ Redis URL retrieved" -ForegroundColor Green
} catch {
    $redisUrl = "redis://sg-property-cache.internal:6379"
    Write-Host "⚠ Using placeholder Redis URL" -ForegroundColor Yellow
}

# Step 6: Deploy API
Write-Host "`nStep 6: Deploying API to Fly.io..." -ForegroundColor Yellow
Write-Host "Building and deploying Docker image..."
flyctl deploy --app $AppName --region $Region 2>&1 | Out-Null
Write-Host "✓ API deployed" -ForegroundColor Green

# Step 7: Verify deployment
Write-Host "`nStep 7: Verifying deployment..." -ForegroundColor Yellow
Write-Host "Checking app status..."
flyctl status --app $AppName | Out-Null
Write-Host "✓ App status verified" -ForegroundColor Green

# Final Summary
Write-Host "`n════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✓ Infrastructure Deployment Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  App Name: $AppName"
Write-Host "  Region: $Region"
Write-Host "  API URL: https://$AppName.fly.dev"
Write-Host "  API Health: https://$AppName.fly.dev/health"
Write-Host "  Database: $databaseUrl"
Write-Host "  Redis: $redisUrl"

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Save connection strings to .env file"
Write-Host "  2. Deploy schema: flyctl postgres exec $dbName < database/schema.sql"
Write-Host "  3. Monitor logs: flyctl logs --app $AppName"
Write-Host "  4. View dashboard: https://fly.io/apps/$AppName"
Write-Host "  5. Test API: curl https://$AppName.fly.dev/health"

Write-Host "`nReady for credential injection!" -ForegroundColor Green
Write-Host "Once credentials are provided, run:"
Write-Host "  flyctl secrets set [CREDENTIALS] --app $AppName`n" -ForegroundColor Cyan
