@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
cd /d C:\Users\ash_f\Desktop\python\sg-property-bot

echo Deploying schema to PostgreSQL cluster nlkxjo5wgmloy93v...
echo.

type database\schema.sql | flyctl postgres connect nlkxjo5wgmloy93v

echo.
echo Deployment completed!
