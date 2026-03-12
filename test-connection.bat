@echo off
echo ========================================
echo Testing Server Connections
echo ========================================
echo.

echo Testing Backend (Flask API)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -UseBasicParsing; Write-Host 'Backend Status: OK' -ForegroundColor Green; Write-Host $response.Content } catch { Write-Host 'Backend Status: FAILED' -ForegroundColor Red; Write-Host $_.Exception.Message }"
echo.

echo Testing Frontend (Next.js)...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -UseBasicParsing; Write-Host 'Frontend Status: OK' -ForegroundColor Green } catch { Write-Host 'Frontend Status: FAILED' -ForegroundColor Red; Write-Host $_.Exception.Message }"
echo.

echo ========================================
echo Test Complete
echo ========================================
echo.
echo If both tests passed, you can access:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:5000
echo.
pause
