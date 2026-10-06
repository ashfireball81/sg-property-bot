#!/bin/bash
# Quick setup for GitHub Actions deployment
# This script helps set up all required secrets for automatic Fly.io deployment

set -e

echo "🔐 SG Property Bot - GitHub Actions Setup"
echo "=========================================="
echo ""

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found!"
    echo "Install from: https://cli.github.com/"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated to GitHub!"
    echo "Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI authenticated"
echo ""

# Get repository
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner' 2>/dev/null || echo "")
if [ -z "$REPO" ]; then
    echo "❌ Not in a Git repository or not a GitHub repo"
    exit 1
fi

echo "📦 Repository: $REPO"
echo ""

# Check if Fly.io authenticated
if ! command -v flyctl &> /dev/null; then
    echo "⚠️  Flyctl not found. Install from: https://fly.io/docs/hands-on/install-flyctl/"
    echo "   Without it, you'll need to manually add FLY_API_TOKEN"
fi

echo "Setting up GitHub Secrets..."
echo ""

# Step 1: FLY_API_TOKEN
echo "1️⃣  Setting up FLY_API_TOKEN"
if command -v flyctl &> /dev/null; then
    if flyctl auth status &> /dev/null; then
        FLY_TOKEN=$(flyctl auth token)
        if [ -n "$FLY_TOKEN" ]; then
            gh secret set FLY_API_TOKEN --body "$FLY_TOKEN" --repo "$REPO"
            echo "✅ FLY_API_TOKEN set successfully"
        else
            echo "❌ Failed to get Fly.io token. Run: flyctl auth login"
        fi
    else
        echo "⚠️  Not authenticated to Fly.io. Run: flyctl auth login"
    fi
else
    echo "⚠️  Flyctl not available. You need to:"
    echo "   1. Get token from: flyctl auth token"
    echo "   2. Run: gh secret set FLY_API_TOKEN --body '<TOKEN>' --repo $REPO"
fi

echo ""

# Step 2: TELEGRAM_BOT_TOKEN
echo "2️⃣  Setting up TELEGRAM_BOT_TOKEN"
read -p "Enter your Telegram Bot Token (from BotFather): " -s TG_BOT_TOKEN
if [ -n "$TG_BOT_TOKEN" ]; then
    gh secret set TELEGRAM_BOT_TOKEN --body "$TG_BOT_TOKEN" --repo "$REPO"
    echo "✅ TELEGRAM_BOT_TOKEN set successfully"
else
    echo "⚠️  Skipped TELEGRAM_BOT_TOKEN"
fi

echo ""

# Step 3: TELEGRAM_CHAT_ID
echo "3️⃣  Setting up TELEGRAM_CHAT_ID"
read -p "Enter your Telegram Chat ID: " TG_CHAT_ID
if [ -n "$TG_CHAT_ID" ]; then
    gh secret set TELEGRAM_CHAT_ID --body "$TG_CHAT_ID" --repo "$REPO"
    echo "✅ TELEGRAM_CHAT_ID set successfully"
else
    echo "⚠️  Skipped TELEGRAM_CHAT_ID"
fi

echo ""

# Verify secrets
echo "Verifying secrets..."
echo ""

if gh secret list --repo "$REPO" | grep -q "FLY_API_TOKEN"; then
    echo "✅ FLY_API_TOKEN configured"
else
    echo "❌ FLY_API_TOKEN not found"
fi

if gh secret list --repo "$REPO" | grep -q "TELEGRAM_BOT_TOKEN"; then
    echo "✅ TELEGRAM_BOT_TOKEN configured"
else
    echo "❌ TELEGRAM_BOT_TOKEN not found"
fi

if gh secret list --repo "$REPO" | grep -q "TELEGRAM_CHAT_ID"; then
    echo "✅ TELEGRAM_CHAT_ID configured"
else
    echo "❌ TELEGRAM_CHAT_ID not found"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Push code: git add . && git commit -m 'feat: add github actions deployment' && git push"
echo "2. Monitor: Go to GitHub → Actions tab"
echo "3. Verify: Check Fly.io logs with: flyctl logs --app sg-property-bot --follow"
echo ""
