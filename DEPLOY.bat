@echo off
REM Automatic Fly.io Deployment Script
REM Run this after: flyctl auth login

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  FLY.IO AUTOMATED DEPLOYMENT
echo ============================================
echo.

REM Check authentication
flyctl auth whoami >nul 2>&1
if errorlevel 1 (
    echo ERROR: Not authenticated
    echo.
    echo Please run: flyctl auth login
    echo.
    pause
    exit /b 1
)

echo OK: Authenticated to Fly.io
echo.
echo Starting deployment...
echo.

REM Step 1: Create app
echo Step 1: Creating app sg-property-bot...
flyctl app create sg-property-bot --region sin 2>nul
echo OK
echo.

REM Step 2: Create PostgreSQL
echo Step 2: Creating PostgreSQL cluster (this takes 2-3 minutes)...
flyctl postgres create --app sg-property-bot --region sin --vm-size shared-cpu-1x 2>nul
echo OK
echo.

REM Step 3: Wait for database
echo Step 3: Waiting for database to be ready...
timeout /t 10 /nobreak
echo.

REM Step 4: Get database credentials
echo Step 4: Getting database credentials...
flyctl postgres info --app sg-property-bot-db > db_info.txt
type db_info.txt | find "Connection string"
del db_info.txt
echo OK
echo.

REM Step 5: Set secrets
echo Step 5: Setting secrets...
flyctl secrets set ^
  DB_HOST=sg-property-bot-db.internal ^
  DB_PORT=5432 ^
  DB_NAME=propertybot ^
  DB_USER=postgres ^
  DB_PASSWORD=temppassword ^
  TELEGRAM_BOT_TOKEN=8864201770:AAGaqUPVsnitvQAlkq1xUrAeWSKdHNFE5WU ^
  TELEGRAM_CHAT_ID=6834628591 ^
  --app sg-property-bot
echo OK
echo.

REM Step 6: Deploy
echo Step 6: Deploying app...
flyctl deploy --app sg-property-bot
echo.

REM Step 7: Status
echo Step 7: Checking status...
echo.
flyctl status --app sg-property-bot
echo.

echo ============================================
echo DEPLOYMENT COMPLETE!
echo ============================================
echo.
echo View logs:
echo   flyctl logs --app sg-property-bot --follow
echo.
echo Configure scheduled job:
echo   See: .github/FLYIO_DEPLOYMENT_STEPS.md (Step 8)
echo.
pause
