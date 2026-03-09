@echo off
REM Bonsai launcher for Miniscope + Syringe
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for miniscope imaging with syringe control.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_miniscope_syringe.bonsai"

REM Run Bonsai with miniscope + syringe configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
