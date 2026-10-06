@echo off
REM Bonsai launcher for Ephys-only recording
REM Accepts command-line arguments: path and rat_name

REM Get command-line arguments with defaults for testing
set "PATH_ARG=%1"
set "RAT_NAME=%2"
set "EPHYS_CHANNELS=%3"

if "%PATH_ARG%"=="" set "PATH_ARG=..\data\experiment_results"
if "%RAT_NAME%"=="" set "RAT_NAME=test"
if "%EPHYS_CHANNELS%"=="" set "EPHYS_CHANNELS=0,1,2,3,4,5,6,7"

set "SCRIPT=%~dp0..\bonsai\bonsai_ephys.bonsai"
set "LAYOUT=%~dp0..\bonsai\bonsai_ephys.layout"

REM Run Bonsai with parameters
bonsai --no-editor --visualizer-layout "%LAYOUT%" -p path="%PATH_ARG%" -p rat_name="%RAT_NAME%" -p EphysChannels="%EPHYS_CHANNELS%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
