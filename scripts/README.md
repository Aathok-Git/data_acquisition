# Bonsai Workflow Scripts

This directory contains batch files (.bat) that launch different Bonsai workflow configurations based on module selections in the main selector.py GUI.

## Naming Convention

Batch files follow a naming pattern based on which modules are selected:

```
bonsai_[module1]_[module2]_[module3]....bat
```

### Core Module Names
- `ephys` - Electrophysiology recording
- `miniscope` - Miniscope imaging
- `analog` - Analog input channels
- `syringe` - Syringe pump control
- `base` - Camera + events only (no core modules selected)

**Note:** Behavioral camera and event logging are always included in all configurations and are not separate toggles.

### Module Selection Examples
- `bonsai_ephys.bat` - Ephys recording only
- `bonsai_miniscope.bat` - Miniscope imaging only
- `bonsai_ephys_miniscope.bat` - Ephys + Miniscope together
- `bonsai_ephys_analog_syringe.bat` - Ephys + Analog + Syringe
- `bonsai_base.bat` - Base recording (camera + events, no other modules)

## Workflow File References

Each .bat file references a corresponding workflow file that should contain the actual Bonsai workflow configuration. The naming pattern for workflow files is:

```
workflow_[same_as_bat_name_without_bonsai_prefix].bonsai
```

### Examples
- `bonsai_ephys.bat` → `workflow_ephys.bonsai`
- `bonsai_ephys_miniscope.bat` → `workflow_ephys_miniscope.bonsai`

**Note:** These workflow files (.bonsai files) are NOT included in this repository and must be created in Bonsai according to your hardware setup and data acquisition requirements.

## Adding New Configurations

To add support for a new module combination:

1. **Create the .bat file** with the appropriate naming convention (use an existing one as a template)
2. **Create the corresponding .bonsai workflow** in Bonsai
3. **Test** by selecting the modules in selector.py and clicking "Launch Bonsai"

### Template

```batch
@echo off
REM Bonsai launcher for [module combination]
REM Update BONSAI_EXE to point to your Bonsai executable.
REM This workflow file should be configured for [description].

set "BONSAI_EXE=C:\Program Files\Bonsai\Bonsai.exe"
set "SCRIPT=%~dp0workflow_[name].bonsai"

REM Run Bonsai with [name] configuration
"%BONSAI_EXE%" "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo Bonsai exited with error %ERRORLEVEL%
)
exit /b %ERRORLEVEL%
```

## Configuration Requirements

Before running any workflow:

1. Update `BONSAI_EXE` path to match your Bonsai installation location
2. Ensure the corresponding `.bonsai` workflow file exists and is properly configured for your hardware
3. Verify hardware drivers are installed (ONIX drivers, etc.)

## Testing

You can test a .bat file directly from the command line:

```cmd
cd scripts
bonsai_ephys.bat
```

## Notes

- Behavioral camera and event logging data are **always included** in every configuration by default
- The selector.py GUI automatically generates the appropriate .bat filename based on module selections
- Only 4 core modules are user-selectable: ephys, miniscope, analog, and syringe
- If a .bat file doesn't exist for a selected combination, an error will be displayed in the GUI
- For complex multi-module setups, consider creating comprehensive workflow templates in Bonsai that can be reused across multiple configurations
- The base configuration (bonsai_base.bat) can be used for behavioral data collection without electrophysiology or imaging
