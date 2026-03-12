@echo off
echo ========================================
echo Pulse Report Scheduler
echo ========================================
echo.
echo Starting automated pulse report scheduler...
echo Schedule: Every 180 minutes (3 hours)
echo Run times: 00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00 IST
echo Recipient: manshuc12@gmail.com
echo Logs: phase6/logs/scheduler.log
echo.
echo Press Ctrl+C to stop the scheduler
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run scheduler
python phase6/scheduler.py

pause
