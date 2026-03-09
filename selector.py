import FreeSimpleGUI as sg
import pandas as pd
import subprocess
from pathlib import Path
from paths import EXPERIMENTS

sg.theme('DarkBlue2')

# ========== CONFIGURATION ==========
# Set to True to allow launching Bonsai without a confirmed experiment line (testing only)
TESTING_MODE_SKIP_EXPERIMENT_CHECK = False
# ====================================

BASE_DIR = Path(__file__).parent

# Global state to track confirmed experiment selection
_confirmed_experiment_line = None


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

    [sg.Text('Hardware Connection:', font=('Helvetica', 12, 'bold'))],
    [sg.Button('Connect Hardware'), sg.Text('Status: Disconnected', key='hw_status')],
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
                subprocess.run([str(script_path)], check=True)
                sg.popup('Bonsai launched successfully')
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
            summary = _process_experiment_row(row)
            # Update display with processing summary
            window['data_display'].update(summary.to_string())
            
            # TRACK: Mark this experiment line as confirmed
            _confirmed_experiment_line = line_idx + 1  # Store 1-based line number
            window['confirmed_status'].update(f'Confirmed Line: {_confirmed_experiment_line}', text_color='green')
            
            # Here you would kick off the real background processing pipeline
            sg.popup('Experiment line confirmed and processing started')
        except Exception as e:
            sg.popup_error(f'Error processing experiment line: {e}')
    
    elif event == 'Connect Hardware':
        # Placeholder for hardware connection
        window['hw_status'].update('Status: Connected')
        sg.popup('Hardware connected successfully')

window.close()