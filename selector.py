import FreeSimpleGUI as sg
import pandas as pd
import subprocess

sg.theme('DarkBlue2')

layout = [
    [sg.Text('Data Acquisition Selector', font=('Helvetica', 16, 'bold'))],
    
    [sg.Text('Select Modules:', font=('Helvetica', 12, 'bold'))],
    [sg.Checkbox('Ephys', key='ephys'), sg.Checkbox('Miniscope', key='miniscope')],
    
    [sg.Button('Launch Bonsai'), sg.Button('Exit')],
    
    [sg.Text('CSV Data Processing:', font=('Helvetica', 12, 'bold'))],
    [sg.Button('Load CSV'), sg.InputText(key='csv_path', size=(30, 1))],
    [sg.Multiline(size=(50, 8), key='data_display', disabled=True)],
    [sg.Button('Process Data')],
    
    [sg.Text('Hardware Connection:', font=('Helvetica', 12, 'bold'))],
    [sg.Button('Connect Hardware'), sg.Text('Status: Disconnected', key='hw_status')],
]

window = sg.Window('Data Acquisition', layout)

while True:
    event, values = window.read()
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    
    elif event == 'Launch Bonsai':
        # Placeholder for Bonsai script
        script_path = 'path/to/bonsai_script.exe'
        try:
            subprocess.run([script_path], check=True)
            sg.popup('Bonsai launched successfully')
        except Exception as e:
            sg.popup_error(f'Error launching Bonsai: {e}')
    
    elif event == 'Load CSV':
        csv_file = sg.popup_get_file('Select CSV file', file_types=(('CSV files', '*.csv'),))
        if csv_file:
            window['csv_path'].update(csv_file)
            try:
                df = pd.read_csv(csv_file)
                window['data_display'].update(df.to_string())
            except Exception as e:
                sg.popup_error(f'Error loading CSV: {e}')
    
    elif event == 'Process Data':
        csv_file = values['csv_path']
        if csv_file:
            try:
                df = pd.read_csv(csv_file)
                # Placeholder data processing
                processed_df = df.describe()
                window['data_display'].update(processed_df.to_string())
                sg.popup('Data processed successfully')
            except Exception as e:
                sg.popup_error(f'Error processing data: {e}')
    
    elif event == 'Connect Hardware':
        # Placeholder for hardware connection
        window['hw_status'].update('Status: Connected')
        sg.popup('Hardware connected successfully')

window.close()