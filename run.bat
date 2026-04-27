@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python scheduler.py --once >> "%~dp0cron.log" 2>&1