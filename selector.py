import FreeSimpleGUI as sg
import pandas as pd
import subprocess
from pathlib import Path
from paths import EXPERIMENTS

sg.theme('DarkBlue2')

# Bonsai script selection based on module choices
BASE_DIR = Path(__file__).parent
_BonsaiScripts = {
    (True, False): BASE_DIR / 'scripts' / 'bonsai_ephys.bat',
    (False, True): BASE_DIR / 'scripts' / 'bonsai_miniscope.bat',
    (True, True): BASE_DIR / 'scripts' / 'bonsai_both.bat',
}

def _select_bonsai_script(ephys: bool, miniscope: bool):
    return _BonsaiScripts.get((bool(ephys), bool(miniscope)))

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

    [sg.Text('Select Modules:', font=('Helvetica', 12, 'bold'))],
    [sg.Checkbox('Ephys', key='ephys'), sg.Checkbox('Miniscope', key='miniscope')],

    [sg.Button('Launch Bonsai'), sg.Button('Exit')],

    [sg.Multiline(size=(50, 8), key='data_display', disabled=True)],

    [sg.Text('Experiment selection:', font=('Helvetica', 12, 'bold'))],
    [sg.Text('Line #:'), sg.InputText(key='line_number', size=(6, 1)), sg.Button('Confirm Line')],

    [sg.Text('Hardware Connection:', font=('Helvetica', 12, 'bold'))],
    [sg.Button('Connect Hardware'), sg.Text('Status: Disconnected', key='hw_status')],
]

window = sg.Window('Data Acquisition', layout)

while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    elif event == 'Launch Bonsai':
        # Select bonsai script based on module choices
        script_path = _select_bonsai_script(values.get('ephys'), values.get('miniscope'))
        if script_path is None:
            sg.popup_error('No Bonsai script for current module selection')
        else:
            try:
                subprocess.run([str(script_path)], check=True)
                sg.popup('Bonsai launched successfully')
            except Exception as e:
                sg.popup_error(f'Error launching Bonsai: {e}')
    
    # CSV is managed via paths.EXPERIMENTS; user provides a line number below
    
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
            # Here you would kick off the real background processing pipeline
            sg.popup('Experiment line confirmed and processing started')
        except Exception as e:
            sg.popup_error(f'Error processing experiment line: {e}')
    
    elif event == 'Connect Hardware':
        # Placeholder for hardware connection
        window['hw_status'].update('Status: Connected')
        sg.popup('Hardware connected successfully')

window.close()