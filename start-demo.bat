@echo off
title Arch Gen AI - Demo Launcher

echo ============================================
echo    ARCH GEN AI - DEMO LAUNCHER
echo ============================================
echo.

REM ---- Sanity checks ----
where python >nul 2>&1 || (echo [X] Python not found in PATH & pause & exit /b 1)
where npm    >nul 2>&1 || (echo [X] npm not found in PATH & pause & exit /b 1)

REM ---- Backend (FastAPI + ML model) ----
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo [!] Backend already running on port 8000 - reusing it.
) else (
    echo [+] Starting backend on http://127.0.0.1:8000 ...
    start "ArchGen Backend" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --port 8000"
)

REM ---- Frontend (Vite dev server) ----
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo [!] Frontend already running on port 5173 - reusing it.
) else (
    echo [+] Starting frontend on http://localhost:5173 ...
    start "ArchGen Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
)

echo.
echo [*] Waiting 10 seconds for servers to boot...
REM ping-based delay: works in any Windows context, unlike timeout.exe
ping -n 11 127.0.0.1 >nul

REM ---- Open the app in the default browser ----
echo [+] Opening browser at http://localhost:5173
start http://localhost:5173

REM ---- Final status check ----
echo.
echo [*] Status:
curl -s -m 5 http://127.0.0.1:8000/health 2>nul | findstr "ok" >nul 2>&1 && echo   [OK] Backend  - http://127.0.0.1:8000 || echo   [??] Backend not responding yet - check the Backend window
curl -s -m 5 -o nul -w "%%{http_code}" http://localhost:5173 2>nul | findstr "200" >nul 2>&1 && echo   [OK] Frontend - http://localhost:5173 || echo   [??] Frontend not responding yet - check the Frontend window

echo.
echo ============================================
echo    READY FOR DEMO
echo    Two windows opened: Backend + Frontend.
echo    Keep them open - closing them stops the app.
echo    To stop everything later: run stop-demo.bat
echo ============================================
echo.
pause
