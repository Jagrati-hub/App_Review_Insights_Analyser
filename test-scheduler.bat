@echo off
echo ========================================
echo Testing Pulse Scheduler
echo ========================================
echo.
echo Running pulse generation immediately (test mode)...
echo This will generate a report right now without waiting for the schedule.
echo Logs: phase6/logs/scheduler.log
echo.
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run scheduler in test mode
python phase6/scheduler.py --test

echo.
echo ========================================
echo Test complete!
echo Check phase6/reports/ for generated files
echo Check phase6/logs/scheduler.log for logs
echo ========================================
pause
