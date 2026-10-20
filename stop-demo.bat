@echo off
title Arch Gen AI - Stop Servers

echo ============================================
echo    ARCH GEN AI - STOP SERVERS
echo ============================================
echo.

for %%p in (8000 5173) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p" ^| findstr "LISTENING"') do (
        echo [+] Stopping process %%a on port %%p
        taskkill /F /PID %%a >nul 2>&1
    )
)

echo.
echo Done. Both servers stopped.
echo.
pause
