@echo off
REM Bonsai launcher for Analog Inputs only
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for analog input data acquisition.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_analog.bonsai"

REM Run Bonsai with analog inputs configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
