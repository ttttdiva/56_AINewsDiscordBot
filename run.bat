@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if "%~1"=="" (
    set "MODE=schedule"
) else (
    set "MODE=%~1"
)

python -m src.main --mode %MODE%
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
