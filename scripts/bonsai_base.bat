@echo off
REM Bonsai launcher for base configuration (events + behavioral camera only)
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for base event logging and camera recording.

set "SCRIPT=%~dp0..\bonsai\bonsai_base.bonsai"
set "LAYOUT=%~dp0..\bonsai\bonsai_base.layout"

REM Run Bonsai with base configuration headless
bonsai --no-editor --visualizer-layout "%LAYOUT%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
