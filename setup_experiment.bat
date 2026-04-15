@echo off
REM Experiment Setup GUI Launcher
REM Activates the data_acquisition conda environment and launches the experiment selector GUI

setlocal enabledelayedexpansion

REM Get the directory where this script is located
cd /d "%~dp0"

REM Activate conda environment and run selector.py
set "TEMP_OUTPUT=%TEMP%\conda_activate_output.txt"
call conda activate data_acquisition >"%TEMP_OUTPUT%" 2>&1
set "ACTIVATE_ERRORLEVEL=%ERRORLEVEL%"

findstr /C:"conda init" "%TEMP_OUTPUT%" >nul
if %ERRORLEVEL% EQU 0 (
    echo Detected conda init requirement. Running conda init.
    call conda init cmd.exe
    if %ERRORLEVEL% NEQ 0 (
        echo Error: conda init failed
        type "%TEMP_OUTPUT%"
        del "%TEMP_OUTPUT%"
        pause
        exit /b %ERRORLEVEL%
    )
    echo Conda initialization completed.
    echo Please close and reopen this terminal, then rerun this script.
    del "%TEMP_OUTPUT%"
    pause
    exit /b 0
)

if %ACTIVATE_ERRORLEVEL% NEQ 0 (
    echo Error: Failed to activate conda environment
    type "%TEMP_OUTPUT%"
    del "%TEMP_OUTPUT%"
    pause
    exit /b %ACTIVATE_ERRORLEVEL%
)

del "%TEMP_OUTPUT%"

REM Run the selector GUI
python selector.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: selector.py exited with error %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

endlocal
