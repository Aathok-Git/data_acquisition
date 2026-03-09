@echo off
REM Bonsai launcher (Ephys-only visualizers)
REM Update BONSAI_EXE to point to your Bonsai executable.
REM Place the actual .bonsai script next to this .bat (same folder) or update SCRIPT variable.

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"

set "SCRIPT=%~dp0bonsai_onix.bonsai"

REM Run Bonsai in headless mode and enable only the Ephys visualizer.
REM The following flags are placeholders — adjust to match your Bonsai CLI.
"%BONSAI_EXE%" --headless --script "%SCRIPT%" --visualizer EphysVisualizer

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
