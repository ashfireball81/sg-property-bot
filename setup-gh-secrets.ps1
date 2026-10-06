#!/usr/bin/env pwsh
# GitHub Secrets Setup Script for sg-property-bot
# This script sets up all required GitHub Secrets for automated Fly.io deployment

param(
    [string]$FlyToken,
    [string]$TelegramBotToken,
    [string]$TelegramChatId
)

Write-Host "====================================================================="
Write-Host "Authenticating and Setting GitHub Secrets for sg-property-bot"
Write-Host "====================================================================="
Write-Host ""

# Step 1: Check GitHub CLI
Write-Host "Step 1: Checking GitHub CLI..."
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI not installed. Install from: https://cli.github.com/"
    exit 1
}
Write-Host "OK - GitHub CLI is installed"
Write-Host ""

# Step 2: Check if gh needs authentication first  
Write-Host "Step 2: Checking GitHub CLI authentication..."
try {
    $authStatus = & gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Not authenticated"
    }
} catch {
    Write-Host "Not authenticated to GitHub"
    Write-Host ""
    Write-Host "Running: gh auth login"
    Write-Host ""
    & gh auth login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to authenticate"
        exit 1
    }
}
Write-Host "OK - Authenticated to GitHub"
Write-Host ""

# Get the repo
Write-Host "Step 3: Setting up secrets for repository..."
$repoPath = Get-Location | Select-Object -ExpandProperty Path
$repoName = Split-Path $repoPath -Leaf

Write-Host "Repository: $repoName"
Write-Host ""

# Create secretsHashtable
$secrets = @{
    "FLY_API_TOKEN" = $FlyToken
    "TELEGRAM_BOT_TOKEN" = $TelegramBotToken
    "TELEGRAM_CHAT_ID" = $TelegramChatId
}

Write-Host "Step 4: Setting GitHub Secrets..."
Write-Host ""

foreach ($secret in $secrets.GetEnumerator()) {
    $secretName = $secret.Name
    $secretValue = $secret.Value
    
    if ([string]::IsNullOrEmpty($secretValue)) {
        Write-Host "Skipping $secretName (empty value)"
        continue
    }
    
    Write-Host "Setting $secretName ..."
    $secretValue | & gh secret set $secretName 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "OK - $secretName configured"
    } else {
        Write-Host "ERROR - Failed to set $secretName"
    }
}

Write-Host ""
Write-Host "Step 5: Verifying secrets..."
Write-Host ""
& gh secret list
Write-Host ""
Write-Host "====================================================================="
Write-Host "Setup Complete!"
Write-Host "====================================================================="
Write-Host ""
Write-Host "Next: Push code to trigger automated deployment"
Write-Host "   git add ."
Write-Host "   git commit -m ""test: trigger deployment"""
Write-Host "   git push origin master"
Write-Host ""
