import FreeSimpleGUI as sg
import pandas as pd
import subprocess
import sys
from pathlib import Path
from paths import EXPERIMENTS, OUTPUT_DIR
import re
import serial
import time

# ========== CONFIGURATION ==========
TESTING_MODE_SKIP_EXPERIMENT_CHECK = False
# ====================================

# Constants
COM_PORT = 'COM4'
BAUD_RATE = 115200
SERIAL_TIMEOUT = 2
SCRIPTS_DIR = Path(__file__).parent / 'scripts'


class ExperimentState:
    """Manages the state of confirmed experiment selection."""

    def __init__(self):
        self.line_number = None
        self.rat_name = None
        self.infusion_rate = None
        self.total_systemic_time = None

    def is_confirmed(self):
        return self.line_number is not None

    def reset(self):
        self.line_number = None
        self.rat_name = None
        self.infusion_rate = None
        self.total_systemic_time = None

    def confirm(self, line_number, rat_name, infusion_rate, total_time):
        self.line_number = line_number
        self.rat_name = rat_name
        self.infusion_rate = infusion_rate
        self.total_systemic_time = total_time


def generate_bonsai_script_name(ephys: bool, miniscope: bool, analog_inputs: bool,
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


def select_bonsai_script(ephys: bool, miniscope: bool, analog_inputs: bool,
                         syringe_use: bool) -> Path:
    """Select the appropriate Bonsai script based on module selections."""
    script_name = generate_bonsai_script_name(ephys, miniscope, analog_inputs, syringe_use)
    return SCRIPTS_DIR / script_name


def process_experiment_row(row: pd.Series) -> str:
    """Process experiment row data and return summary string."""
    try:
        summary = row.to_frame().T.describe(include='all')
    except Exception:
        summary = row.to_frame().T
    return summary.to_string()


def parse_float(value) -> float | None:
    """Safely parse a value to float, returning None if invalid."""
    try:
        result = float(value)
        return None if pd.isna(result) else result
    except (TypeError, ValueError):
        return None


def calculate_infusion_rate(row: pd.Series) -> float | None:
    """Calculate infusion rate in mL/min from experiment CSV values."""
    weight = parse_float(row.get('rat weight (kg)'))
    dose = parse_float(row.get('systemic dose (% or mg/kg/min)'))
    concentration = parse_float(row.get('systemic drug concentration (mg/mL)'))

    if None in (weight, dose, concentration) or concentration == 0:
        return None

    # infusion rate (mL/min) = dose (mg/kg/min) * weight (kg) / concentration (mg/mL)
    return dose * weight / concentration


class SyringeController:
    """Handles syringe pump communication and control."""

    def __init__(self, port=COM_PORT, baud=BAUD_RATE, timeout=SERIAL_TIMEOUT):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.serial_conn = None

    def connect(self):
        """Connect to the syringe pump."""
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=self.timeout)
            time.sleep(0.1)  # Allow connection to stabilize
            return True
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None

    def prepare_commands(self, infusion_rate: float, total_time_seconds: float = None) -> list[str]:
        """Build syringe pump commands for the PHD Ultra."""
        if infusion_rate is None:
            return []

        commands = [
            f'irate {infusion_rate:.3f} ml/min',
            'citime 0',  # Continuous infusion
        ]

        if total_time_seconds is not None:
            commands.append(f'ttime {int(total_time_seconds)}')

        return commands

    def validate_command(self, command: str) -> tuple[bool, str]:
        """Validate a single syringe pump command string."""
        if not isinstance(command, str) or not command.strip():
            return False, 'Command is empty'

        parts = command.strip().lower().split()
        if parts[0] == 'irate':
            if len(parts) != 3 or parts[2] != 'ml/min':
                return False, 'irate must use syntax: irate <rate> ml/min'
            try:
                rate = float(parts[1])
                if rate <= 0:
                    return False, 'irate value must be positive'
            except ValueError:
                return False, 'irate value must be a number'
            return True, ''

        if parts[0] == 'citime':
            if len(parts) != 2 or parts[1] != '0':
                return False, 'citime must use syntax: citime 0'
            return True, ''

        if parts[0] == 'ttime':
            if len(parts) != 2:
                return False, 'ttime must use syntax: ttime <seconds>'
            if not parts[1].isdigit():
                return False, 'ttime seconds must be an integer'
            return True, ''

        return False, f'Unknown command: {parts[0]}'

    def validate_commands(self, commands: list[str]) -> tuple[bool, str]:
        """Validate a list of syringe pump commands before sending."""
        for command in commands:
            valid, message = self.validate_command(command)
            if not valid:
                return False, message
        return True, ''

    def send_commands(self, commands: list[str], window) -> bool:
        """Send commands to the syringe pump and update GUI status."""
        if not self.serial_conn:
            window['pump_status'].update('Error: No serial connection')
            return False

        valid, error_message = self.validate_commands(commands)
        if not valid:
            window['pump_status'].update(f'Invalid syringe command: {error_message}', text_color='red')
            return False

        try:
            for cmd in commands:
                # Send command with carriage return
                self.serial_conn.write((cmd + '\r').encode('ascii'))
                window['pump_status'].update(f'Sent: {cmd}')
                window.refresh()

                # Wait for response
                time.sleep(0.2)

                # Read response if available
                if self.serial_conn.in_waiting:
                    response = self.serial_conn.readline().decode('ascii').strip()
                    if response:
                        window['pump_status'].update(f'Response: {response}')
                        window.refresh()

            return True
        except Exception as e:
            window['pump_status'].update(f'Error: {str(e)}')
            return False


def create_layout():
    """Create the GUI layout."""
    return [
        [sg.Text('ONIX Experiment Selector', font=('Helvetica', 16, 'bold'))],

        [sg.Text('Select Core Recording Type(s):', font=('Helvetica', 12, 'bold'))],
        [sg.Checkbox('Ephys', key='ephys'), sg.Checkbox('Miniscope', key='miniscope')],

        [sg.Text('Select Optional Modules:', font=('Helvetica', 12, 'bold'))],
        [sg.Checkbox('Analog Inputs', key='analog_inputs'), sg.Checkbox('Syringe Use', key='syringe_use')],

        
        [sg.Multiline(size=(50, 8), key='data_display', disabled=True)],

        [sg.Text('Experiment selection:', font=('Helvetica', 12, 'bold'))],
        [sg.Text('Line #:'), sg.InputText(key='line_number', size=(6, 1)), sg.Button('Confirm Line')],
        [sg.Text('Confirmed Line: None', key='confirmed_status', text_color='orange')],
        [sg.Text('Infusion Rate (mL/min): None', key='infusion_status', text_color='orange')],
        [sg.Text('Pump Status: Idle', key='pump_status', text_color='orange')],
        [sg.Button('Launch Bonsai'), sg.Button('Exit'), sg.Button('📁', key='open_output_folder', tooltip='Open experiment output folder')],

    ]


def open_output_folder(window):
    """Open the output directory in the system file explorer."""
    try:
        target_path = Path(OUTPUT_DIR)
        target_path.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith('darwin'):
            subprocess.run(['open', str(target_path)], check=True)
        elif sys.platform.startswith('win'):
            subprocess.run(['explorer', str(target_path)], check=True)
        else:
            subprocess.run(['xdg-open', str(target_path)], check=True)
    except Exception as e:
        sg.popup_error(f'Unable to open output folder: {e}')


def handle_confirm_line(values, window, state: ExperimentState):
    """Handle the Confirm Line button event."""
    line_str = values.get('line_number')
    try:
        line_idx = int(line_str) - 1
        if line_idx < 0:
            raise ValueError('Line number must be >= 1')
    except Exception as e:
        sg.popup_error(f'Invalid line number: {e}')
        return

    try:
        exp_path = Path(EXPERIMENTS)
        df_exp = pd.read_csv(exp_path)
        if line_idx >= len(df_exp):
            sg.popup_error('Line number out of range')
            return

        row = df_exp.iloc[line_idx]

        # Extract data
        rat_name = row.get('id', 'unknown')
        infusion_rate = calculate_infusion_rate(row)
        has_valid_rate = infusion_rate is not None and not pd.isna(infusion_rate)
        infusion_text = f'{infusion_rate:.3f}' if has_valid_rate else 'No drug'

        # Extract total systemic time
        total_systemic_time_sec = None
        if has_valid_rate:
            total_time_min = parse_float(row.get('total systemic time (min)'))
            if total_time_min and total_time_min > 0:
                total_systemic_time_sec = int(total_time_min * 60)

        # Update GUI
        summary = process_experiment_row(row)
        window['data_display'].update(summary)
        window['infusion_status'].update(f'Infusion Rate (mL/min): {infusion_text}',
                                        text_color='green' if has_valid_rate else 'orange')

        # Confirm the experiment
        state.confirm(line_idx + 1, str(rat_name), infusion_rate, total_systemic_time_sec)
        window['confirmed_status'].update(f'Confirmed Line: {state.line_number}', text_color='green')

        # Handle syringe checkbox
        if not has_valid_rate:
            window['syringe_use'].update(disabled=True, value=False)
            window['pump_status'].update('Insufficient infusion data: syringe unavailable', text_color='red')
        else:
            window['syringe_use'].update(disabled=False)
            window['pump_status'].update('Syringe available - ready for configuration', text_color='green')

        sg.popup('Experiment line confirmed')

    except Exception as e:
        sg.popup_error(f'Error processing experiment line: {e}')


def handle_launch_bonsai(values, window, state: ExperimentState):
    """Handle the Launch Bonsai button event."""
    # Check experiment confirmation
    if not state.is_confirmed() and not TESTING_MODE_SKIP_EXPERIMENT_CHECK:
        sg.popup_error('ERROR: No experiment line confirmed!\n\n'
                      'Please enter a line number from experiments.csv and click '
                      '"Confirm Line" before launching Bonsai.\n\n'
                      'To disable this check for testing, set TESTING_MODE_SKIP_EXPERIMENT_CHECK = True')
        return

    # Select script
    script_path = select_bonsai_script(
        values.get('ephys', False),
        values.get('miniscope', False),
        values.get('analog_inputs', False),
        values.get('syringe_use', False)
    )

    if not script_path.exists():
        sg.popup_error(f'Bonsai script not found:\n{script_path}\n\n'
                      'Please ensure the corresponding .bat file exists in scripts/')
        return

    # Handle syringe setup if needed
    if values.get('syringe_use', False):
        syringe = SyringeController()
        window['pump_status'].update('Connecting to syringe pump...')
        window.refresh()

        if not syringe.connect():
            window['pump_status'].update('Failed to connect to syringe pump')
            window.refresh()
            sg.popup_error('Failed to connect to syringe pump on COM4. Check connection and try again.')
            return

        window['pump_status'].update('Preparing syringe pump parameters...')
        window.refresh()

        commands = syringe.prepare_commands(state.infusion_rate, state.total_systemic_time)
        success = syringe.send_commands(commands, window)

        if success:
            window['pump_status'].update('Syringe parameters ready')
        else:
            window['pump_status'].update('Error configuring syringe')
            syringe.disconnect()
            sg.popup_error('Failed to send commands to syringe pump. Check pump status and try again.')
            return

        syringe.disconnect()

    # Launch Bonsai
    try:
        base_path = str(OUTPUT_DIR)
        rat_name = state.rat_name or 'test'
        subprocess.run([str(script_path), base_path, rat_name], check=True)
        sg.popup('Bonsai launched successfully')
    except Exception as e:
        sg.popup_error(f'Error launching Bonsai: {e}')


def main():
    """Main application entry point."""
    sg.theme('DarkBlue2')

    layout = create_layout()
    window = sg.Window('Data Acquisition', layout)
    state = ExperimentState()

    while True:
        event, values = window.read()

        if event == sg.WINDOW_CLOSED or event == 'Exit':
            break
        elif event == 'Confirm Line':
            handle_confirm_line(values, window, state)
        elif event == 'Launch Bonsai':
            handle_launch_bonsai(values, window, state)
        elif event == 'open_output_folder':
            open_output_folder(window)

    window.close()


if __name__ == '__main__':
    main()

