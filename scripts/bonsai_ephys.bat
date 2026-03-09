@echo off
REM Bonsai launcher for Ephys-only recording
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for ephys data acquisition.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_ephys.bonsai"

REM Run Bonsai with ephys-only configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
