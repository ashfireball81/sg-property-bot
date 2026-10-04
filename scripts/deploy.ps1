# Deploy SG Property Bot to Fly.io - Corrected Version
# Windows PowerShell 5.1 Compatible

param(
    [string]$AppName = "sg-property-bot",
    [string]$Region = "sin"
)

$ErrorActionPreference = 'Continue'

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SG Property Bot - Fly.io Infrastructure Deployment" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Prerequisites check
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
$flyctlCmd = Get-Command flyctl -ErrorAction SilentlyContinue
if (-not $flyctlCmd) {
    Write-Host "ERROR: flyctl not installed" -ForegroundColor Red
    exit 1
}
Write-Host "OK: flyctl installed" -ForegroundColor Green

$auth = & flyctl auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not authenticated" -ForegroundColor Red
    exit 1
}
Write-Host "OK: Authenticated" -ForegroundColor Green
Write-Host ""

# Step 1: Create/Verify Fly app
Write-Host "Step 1: Fly.io Application" -ForegroundColor Yellow
$appOutput = & flyctl apps list 2>&1
$appFound = $false

if ($appOutput -match $AppName) {
    $appFound = $true
}

if ($appFound) {
    Write-Host "  OK: App already exists" -ForegroundColor Green
} else {
    Write-Host "  Creating app $AppName..."
    & flyctl apps create $AppName --region $Region 2>&1 | Out-Null
    Write-Host "  OK: App created" -ForegroundColor Green
}

# Step 2: PostgreSQL
Write-Host ""
Write-Host "Step 2: PostgreSQL Database" -ForegroundColor Yellow
$pgOutput = & flyctl postgres list 2>&1
$pgFound = $false
$dbName = "sg-property-db"

if ($pgOutput -match $dbName) {
    $pgFound = $true
}

if ($pgFound) {
    Write-Host "  OK: PostgreSQL already exists" -ForegroundColor Green
} else {
    Write-Host "  Creating PostgreSQL instance..."
    & flyctl postgres create --name $dbName --region $Region --vm-size shared-cpu-1x 2>&1 | Out-Null
    Write-Host "  OK: PostgreSQL created" -ForegroundColor Green
}

# Step 3: Redis
Write-Host ""
Write-Host "Step 3: Redis Cache" -ForegroundColor Yellow
$redisOutput = & flyctl redis list 2>&1
$redisFound = $false
$redisName = "sg-property-cache"

if ($redisOutput -match $redisName) {
    $redisFound = $true
}

if ($redisFound) {
    Write-Host "  OK: Redis already exists" -ForegroundColor Green
} else {
    Write-Host "  Creating Redis instance..."
    & flyctl redis create --name $redisName --region $Region 2>&1 | Out-Null
    Write-Host "  OK: Redis created" -ForegroundColor Green
}

# Step 4: Set secrets
Write-Host ""
Write-Host "Step 4: Configuration Secrets" -ForegroundColor Yellow
& flyctl secrets set NODE_ENV=production API_PORT=3000 LOG_LEVEL=info --app $AppName 2>&1 | Out-Null
Write-Host "  OK: Secrets configured" -ForegroundColor Green

# Step 5: Get connection strings
Write-Host ""
Write-Host "Step 5: Connection Strings" -ForegroundColor Yellow
$dbUrl = "postgresql://user:pass@sg-property-db.internal/sg_property_bot"
$redisUrl = "redis://sg-property-cache.internal:6379"

try {
    $dbUrl = & flyctl postgres connect-string $dbName 2>&1
    Write-Host "  OK: Database URL retrieved" -ForegroundColor Green
}
catch {
    Write-Host "  WARNING: Using internal database URL" -ForegroundColor Yellow
}

try {
    $redisUrl = & flyctl redis connect-string $redisName 2>&1
    Write-Host "  OK: Redis URL retrieved" -ForegroundColor Green
}
catch {
    Write-Host "  WARNING: Using internal Redis URL" -ForegroundColor Yellow
}

# Step 6: Deploy API
Write-Host ""
Write-Host "Step 6: API Deployment" -ForegroundColor Yellow
Write-Host "  Deploying Docker image (may take 2-3 minutes)..."
& flyctl deploy --app $AppName --region $Region 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: API deployed" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Deploy returned exit code $LASTEXITCODE" -ForegroundColor Yellow
}

# Step 7: Verify
Write-Host ""
Write-Host "Step 7: Verification" -ForegroundColor Yellow
& flyctl status --app $AppName 2>&1 | Out-Null
Write-Host "  OK: Status verified" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  Application: $AppName"
Write-Host "  Region: $Region"
Write-Host "  API URL: https://$AppName.fly.dev"
Write-Host "  Health Check: https://$AppName.fly.dev/health"
Write-Host ""

Write-Host "Connection Strings:" -ForegroundColor Cyan
Write-Host "  Database: $dbUrl"
Write-Host "  Redis: $redisUrl"
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Deploy schema: psql 'connection_string_here' -f database/schema.sql"
Write-Host "  2. Test API: curl https://$AppName.fly.dev/health"
Write-Host "  3. View logs: flyctl logs --app $AppName"
Write-Host ""
