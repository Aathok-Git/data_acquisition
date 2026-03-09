@echo off
REM Experiment Setup GUI Launcher
REM Activates the data_acquisition conda environment and launches the experiment selector GUI

setlocal enabledelayedexpansion

REM Get the directory where this script is located
cd /d "%~dp0"

REM Activate conda environment and run selector.py
call conda activate data_acquisition
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate conda environment
    pause
    exit /b %ERRORLEVEL%
)

REM Run the selector GUI
python selector.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: selector.py exited with error %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

endlocal
