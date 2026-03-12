@echo off
echo ========================================
echo Play Store Review Analyzer
echo Starting Backend and Frontend...
echo ========================================
echo.
echo Backend will start on: http://localhost:5000
echo Frontend will start on: http://localhost:3000
echo.
echo Press Ctrl+C in each window to stop the servers
echo ========================================
echo.

REM Start backend in new window
start "Backend - Flask API" cmd /k "start-backend.bat"

REM Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

REM Start frontend in new window
start "Frontend - Next.js" cmd /k "start-frontend.bat"

echo.
echo Both servers are starting...
echo Check the new windows for server status
echo.
pause
