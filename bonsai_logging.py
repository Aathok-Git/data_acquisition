"""
Bonsai logging GUI using PySimpleGUI
This module provides a GUI window for message logging that integrates with Bonsai workflows.
The state variable can be accessed and used by Bonsai's Python object nodes.
"""

import FreeSimpleGUI as sg
import threading
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoggingState:
    """State container for logging messages"""
    message: str = ""
    submitted: bool = False


class BonsaiLogger:
    """
    A GUI-based logger for use with Bonsai scripting.
    
    Usage in Bonsai:
    1. Create a Python object node with: logger = BonsaiLogger()
    2. Start the GUI with: logger.start()
    3. Access the current message: logger.state.message
    4. Check if message was submitted: logger.state.submitted
    5. Stop the GUI with: logger.stop()
    """
    
    def __init__(self, window_title: str = "Bonsai Logger"):
        """
        Initialize the BonsaiLogger.
        
        Args:
            window_title: Title of the GUI window
        """
        self.state = LoggingState()
        self.window_title = window_title
        self.window: Optional[sg.Window] = None
        self.thread: Optional[threading.Thread] = None
        self.running = False
        
        # Set PySimpleGUI theme
        sg.theme('DarkBlue2')
    
    def _create_layout(self):
        """Create the GUI layout"""
        layout = [
            [sg.Text('Enter message:', font=('Any', 12, 'bold'))],
            [sg.Multiline(size=(40, 5), key='-MESSAGE-', font=('Any', 10))],
            [sg.Button('Submit', size=(10, 1)), sg.Button('Clear', size=(10, 1)), sg.Button('Exit', size=(10, 1))],
            [sg.Text('Last Message:', font=('Any', 10, 'bold'))],
            [sg.Multiline(size=(40, 3), key='-DISPLAY-', disabled=True, font=('Any', 9))]
        ]
        return layout
    
    def _run_gui(self):
        """Run the GUI loop in a separate thread"""
        self.window = sg.Window(self.window_title, self._create_layout())
        self.running = True
        
        while self.running:
            try:
                event, values = self.window.read(timeout=100)
                
                if event == sg.WINDOW_CLOSED or event == 'Exit':
                    self.running = False
                    break
                
                elif event == 'Submit':
                    message = values['-MESSAGE-'].strip()
                    if message:
                        self.state.message = message
                        self.state.submitted = True
                        self.window['-DISPLAY-'].update(f"Submitted: {message}")
                        self.window['-MESSAGE-'].update("")
                
                elif event == 'Clear':
                    self.window['-MESSAGE-'].update("")
                    self.state.submitted = False
            
            except Exception as e:
                print(f"Error in GUI loop: {e}")
                self.running = False
        
        if self.window:
            self.window.close()
    
    def start(self):
        """Start the GUI in a separate daemon thread"""
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._run_gui, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the GUI"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def get_message(self) -> str:
        """
        Get the current message from the state.
        
        Returns:
            The current message string
        """
        return self.state.message
    
    def reset_submitted_flag(self):
        """Reset the submitted flag after processing"""
        self.state.submitted = False


# For standalone testing
if __name__ == '__main__':
    logger = BonsaiLogger()
    logger.start()
    
    # Keep the program running
    import time
    try:
        while True:
            time.sleep(0.1)
            if logger.state.submitted:
                print(f"Message received: {logger.state.message}")
                logger.reset_submitted_flag()
    except KeyboardInterrupt:
        print("Shutting down...")
        logger.stop()
