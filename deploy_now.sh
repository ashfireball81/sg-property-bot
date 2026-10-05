#!/bin/bash
# Deploy schema via flyctl postgres connect

echo "🚀 DEPLOYING SCHEMA VIA FLYCTL POSTGRES"
echo "========================================"
echo ""

cd /c/Users/ash_f/Desktop/python/sg-property-bot

echo "Connecting to PostgreSQL and executing schema..."
echo ""

# Use flyctl to connect and pipe the schema file
flyctl postgres connect nlkxjo5wgmloy93v < database/schema.sql

echo ""
echo "========================================"
echo "✅ Deployment command executed"
echo "========================================"
