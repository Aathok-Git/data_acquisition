import FreeSimpleGUI as sg
import pandas as pd
import subprocess
from pathlib import Path
from paths import EXPERIMENTS
import serial
import time

sg.theme('DarkBlue2')

# ========== CONFIGURATION ==========
# Set to True to allow launching Bonsai without a confirmed experiment line (testing only)
TESTING_MODE_SKIP_EXPERIMENT_CHECK = False
# ====================================

BASE_DIR = Path(__file__).parent

# Global state to track confirmed experiment selection
_confirmed_experiment_line = None
_confirmed_rat_name = None
_confirmed_infusion_rate = None
_data_base_path = BASE_DIR / 'data' / 'experiment_results'


def _generate_bonsai_script_name(ephys: bool, miniscope: bool, analog_inputs: bool, 
                                 syringe_use: bool) -> str:
    """
    Generate a bat file name based on module selections.
    Uses naming convention: bonsai_<module1>_<module2>_....bat
    Behavioral camera and event logging are always included in all configurations.
    """
    modules = []
    if ephys:
        modules.append("ephys")
    if miniscope:
        modules.append("miniscope")
    if analog_inputs:
        modules.append("analog")
    if syringe_use:
        modules.append("syringe")
    
    # If no modules selected, use base (camera and events always present)
    if not modules:
        return "bonsai_base.bat"
    
    return "bonsai_" + "_".join(modules) + ".bat"


def _select_bonsai_script(ephys: bool, miniscope: bool, analog_inputs: bool, 
                         syringe_use: bool):
    """Select the appropriate Bonsai script based on module selections."""
    script_name = _generate_bonsai_script_name(ephys, miniscope, analog_inputs, 
                                               syringe_use)
    script_path = BASE_DIR / 'scripts' / script_name
    return script_path

def _process_experiment_row(row: pd.Series):
    # Placeholder: heavy data processing happens here
    # For now, summarize numeric values and return a short string
    try:
        summary = row.to_frame().T.describe(include='all')
    except Exception:
        summary = row.to_frame().T
    return summary


def _parse_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _calculate_infusion_rate(row: pd.Series):
    """Calculate infusion rate in mL/min from experiment CSV values."""
    weight = _parse_float(row.get('rat weight (kg)'))
    dose = _parse_float(row.get('systemic dose (% or mg/kg/min)'))
    concentration = _parse_float(row.get('systemic drug concentration (mg/mL)'))

    if weight is None or dose is None or concentration is None or concentration == 0:
        return None

    # infusion rate (mL/min) = dose (mg/kg/min) * weight (kg) * drug dilution (mL/mg)
    # When concentration is given as mg/mL, the dilution is 1 / concentration.
    return dose * weight / concentration


def _connect_to_syringe():
    """Connect to PHD Ultra syringe pump via serial."""
    try:
        ser = serial.Serial('COM4', 115200, timeout=2)
        time.sleep(0.1)  # Allow connection to stabilize
        return ser
    except serial.SerialException as e:
        print(f"Serial connection error: {e}")
        return None


def _prepare_syringe_commands(infusion_rate: float):
    """Build syringe pump commands for the PHD Ultra."""
    if infusion_rate is None:
        return []

    # PHD Ultra commands:
    # irate <rate> - set infusion rate in mL/min
    # citime <time> - set continuous infusion time in minutes (0 = continuous)
    # ttime <time> - set total time in minutes (0 = continuous)
    return [
        f'irate {infusion_rate:.3f}',
        'citime 0',  # Continuous infusion
        'ttime 0',   # Continuous total time
    ]


def _update_syringe_parameters(ser, commands, window):
    """Send syringe commands to PHD Ultra and update GUI status."""
    if not ser:
        window['pump_status'].update('Error: No serial connection')
        return False

    try:
        for cmd in commands:
            # Send command with carriage return
            ser.write((cmd + '\r').encode('ascii'))
            window['pump_status'].update(f'Sent: {cmd}')
            window.refresh()

            # Wait for response (adjust timeout as needed)
            time.sleep(0.2)

            # Read response if available
            if ser.in_waiting:
                response = ser.readline().decode('ascii').strip()
                if response:
                    window['pump_status'].update(f'Response: {response}')
                    window.refresh()

        return True

    except Exception as e:
        window['pump_status'].update(f'Error: {str(e)}')
        return False


layout = [
    [sg.Text('ONIX Experiment Selector', font=('Helvetica', 16, 'bold'))],

    [sg.Text('Select Core Recording Type(s):', font=('Helvetica', 12, 'bold'))],
    [sg.Checkbox('Ephys', key='ephys'), sg.Checkbox('Miniscope', key='miniscope')],
    
    [sg.Text('Select Optional Modules:', font=('Helvetica', 12, 'bold'))],
    [sg.Checkbox('Analog Inputs', key='analog_inputs'), sg.Checkbox('Syringe Use', key='syringe_use')],

    [sg.Button('Launch Bonsai'), sg.Button('Exit')],

    [sg.Multiline(size=(50, 8), key='data_display', disabled=True)],

    [sg.Text('Experiment selection:', font=('Helvetica', 12, 'bold'))],
    [sg.Text('Line #:'), sg.InputText(key='line_number', size=(6, 1)), sg.Button('Confirm Line')],
    [sg.Text('Confirmed Line: None', key='confirmed_status', text_color='orange')],
    [sg.Text('Infusion Rate (mL/min): None', key='infusion_status', text_color='orange')],
    [sg.Text('Pump Status: Idle', key='pump_status', text_color='orange')],
]

window = sg.Window('Data Acquisition', layout)

while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    elif event == 'Launch Bonsai':
        # FAILSAFE: Check if a valid experiment line has been confirmed
        if _confirmed_experiment_line is None and not TESTING_MODE_SKIP_EXPERIMENT_CHECK:
            sg.popup_error('ERROR: No experiment line confirmed!\n\n'
                          'Please enter a line number from experiments.csv and click '
                          '"Confirm Line" before launching Bonsai.\n\n'
                          'To disable this check for testing, set TESTING_MODE_SKIP_EXPERIMENT_CHECK = True')
            continue
        
        # Select bonsai script based on all module choices
        script_path = _select_bonsai_script(
            values.get('ephys', False),
            values.get('miniscope', False),
            values.get('analog_inputs', False),
            values.get('syringe_use', False)
        )
        
        if script_path is None or not script_path.exists():
            sg.popup_error(f'Bonsai script not found:\n{script_path}\n\n'
                          'Please ensure the corresponding .bat file exists in scripts/')
        else:
            try:
                # Prepare arguments for the batch file
                # Calculate relative path from scripts directory to experiment_results
                base_path = '..\\data\\experiment_results'
                rat_name = _confirmed_rat_name if _confirmed_rat_name else 'test'
                
                if values.get('syringe_use', False):
                    window['pump_status'].update('Connecting to syringe pump...')
                    window.refresh()
                    ser = _connect_to_syringe()

                    if ser:
                        window['pump_status'].update('Preparing syringe pump parameters...')
                        window.refresh()
                        commands = _prepare_syringe_commands(_confirmed_infusion_rate)
                        success = _update_syringe_parameters(ser, commands, window)
                        if success:
                            window['pump_status'].update('Syringe parameters ready')
                        else:
                            window['pump_status'].update('Error configuring syringe')
                        ser.close()  # Always close the serial connection
                    else:
                        window['pump_status'].update('Failed to connect to syringe pump')
                        window.refresh()
                        sg.popup_error('Failed to connect to syringe pump on COM4. Check connection and try again.')
                        continue  # Don't launch Bonsai if syringe connection failed
                
                # Launch Bonsai with base_path and rat_name arguments
                subprocess.run([str(script_path), base_path, rat_name], check=True)
                sg.popup('Bonsai launched successfully')
                break
            except Exception as e:
                sg.popup_error(f'Error launching Bonsai: {e}')
    
    elif event == 'Confirm Line':
        line_str = values.get('line_number')
        try:
            line_idx = int(line_str) - 1
            if line_idx < 0:
                raise ValueError('Line number must be >= 1')
        except Exception as e:
            sg.popup_error(f'Invalid line number: {e}')
            continue

        try:
            exp_path = Path(EXPERIMENTS)
            df_exp = pd.read_csv(exp_path)
            if line_idx >= len(df_exp):
                sg.popup_error('Line number out of range')
                continue

            row = df_exp.iloc[line_idx]
            
            # Extract rat name from 'id' column (column 2)
            rat_name = row.get('id', 'unknown')
            infusion_rate = _calculate_infusion_rate(row)
            infusion_text = f'{infusion_rate:.3f}' if infusion_rate is not None else 'N/A'
            
            # Display experiment info
            summary = _process_experiment_row(row)
            window['data_display'].update(summary.to_string())
            window['infusion_status'].update(f'Infusion Rate (mL/min): {infusion_text}', text_color='green' if infusion_rate is not None else 'orange')
            
            # TRACK: Mark this experiment line as confirmed with rat name
            _confirmed_experiment_line = line_idx + 1  # Store 1-based line number
            _confirmed_rat_name = str(rat_name)
            _confirmed_infusion_rate = infusion_rate
            
            window['confirmed_status'].update(f'Confirmed Line: {_confirmed_experiment_line}', text_color='green')
            
            sg.popup('Experiment line confirmed')
        except Exception as e:
            sg.popup_error(f'Error processing experiment line: {e}')
    
window.close()