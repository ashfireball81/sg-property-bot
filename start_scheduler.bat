@echo off
REM Start Property Bot Scheduler Daemon
cd /d "%~dp0"
python scheduler.py --start
