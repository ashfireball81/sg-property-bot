@echo off
REM SG Property Bot - Fly.io Deployment Script
REM This script will deploy your bot to Fly.io

echo.
echo ========================================================================
echo                      FLY.IO DEPLOYMENT STEPS
echo ========================================================================
echo.
echo Step 1: Authenticate to Fly.io
echo    flyctl auth login
echo.
echo    After login, continue to Step 2
echo.
echo Step 2: Create Fly.io App (if not exists)
echo    flyctl app create sg-property-bot --region sin
echo.
echo Step 3: Create PostgreSQL Database
echo    flyctl postgres create --app sg-property-bot --region sin
echo.
echo Step 4: Set Secrets
echo    flyctl secrets set ^
echo      DB_HOST=sg-property-bot-db.internal ^
echo      DB_PORT=5432 ^
echo      DB_NAME=propertybot ^
echo      DB_USER=postgres ^
echo      DB_PASSWORD=your_password_here ^
echo      TELEGRAM_BOT_TOKEN=your_token ^
echo      TELEGRAM_CHAT_ID=your_chat_id ^
echo      --app sg-property-bot
echo.
echo Step 5: Deploy App
echo    flyctl deploy --app sg-property-bot
echo.
echo Step 6: Check Status
echo    flyctl status --app sg-property-bot
echo.
echo ========================================================================
echo.
echo To deploy automatically, run:
echo    python deploy_to_flyio.py
echo.
echo For detailed instructions, see:
echo    .github/FLYIO_DEPLOYMENT_STEPS.md
echo.
echo ========================================================================
echo.
