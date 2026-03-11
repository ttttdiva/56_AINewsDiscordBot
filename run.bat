@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

if "%~1"=="" (
    set "MODE=manual"
) else (
    set "MODE=%~1"
)

if "%~2"=="" (
    python -m src.main --mode %MODE%
) else (
    python -m src.main --mode %MODE% --date %~2
)
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /b %EXIT_CODE%
