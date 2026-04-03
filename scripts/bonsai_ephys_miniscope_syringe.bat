@echo off
REM Bonsai launcher for Ephys + Miniscope + Syringe
REM Accepts command-line arguments: path and rat_name

REM Get command-line arguments with defaults for testing
set "PATH_ARG=%1"
set "RAT_NAME=%2"

if "%PATH_ARG%"=="" set "PATH_ARG=..\data\experiment_results"
if "%RAT_NAME%"=="" set "RAT_NAME=test"

set "SCRIPT=%~dp0..\bonsai\bonsai_base.bonsai"
set "LAYOUT=%~dp0..\bonsai\bonsai_base.layout"

REM Run Bonsai with parameters
bonsai --no-editor --visualizer-layout "%LAYOUT%" -p path="%PATH_ARG%" -p rat_name="%RAT_NAME%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
REM Bonsai launcher for Ephys + Miniscope + Syringe
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for ephys + miniscope with syringe control.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_ephys_miniscope_syringe.bonsai"

REM Run Bonsai with ephys + miniscope + syringe configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
