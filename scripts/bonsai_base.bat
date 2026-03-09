@echo off
REM Bonsai launcher for base configuration (events + behavioral camera only)
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for base event logging and camera recording.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_base.bonsai"

REM Run Bonsai with base configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
