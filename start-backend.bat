@echo off
echo ========================================
echo Starting Flask Backend API
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Running with system Python...
)

echo.
echo Starting Flask server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python phase2/ui_controller.py

pause
