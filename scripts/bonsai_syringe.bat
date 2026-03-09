@echo off
REM Bonsai launcher for Syringe Use only
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for syringe pump control.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_syringe.bonsai"

REM Run Bonsai with syringe configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
