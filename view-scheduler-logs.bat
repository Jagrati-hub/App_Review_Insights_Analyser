@echo off
echo ========================================
echo Scheduler Logs Viewer
echo ========================================
echo.
echo Log file: phase6/logs/scheduler.log
echo.
echo ========================================
echo.

if exist phase6\logs\scheduler.log (
    type phase6\logs\scheduler.log
    echo.
    echo ========================================
    echo End of logs
    echo ========================================
) else (
    echo No log file found yet.
    echo The log file will be created when the scheduler runs.
)

echo.
pause
