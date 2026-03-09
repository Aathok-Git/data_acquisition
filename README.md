# data_acquisition

A data acquisition pipeline for the Melonakos Lab at BYU. This system integrates with the ONIX hardware platform and Bonsai workflow engine to control and manage experiments using electrophysiology (ephys), miniscope imaging, and additional analog/behavioral data streams.

## Project Goals

- Provide a unified interface for configuring and launching complex multi-module recording experiments
- Manage experiment metadata and hardware configurations through a CSV-based system
- Enable real-time message logging and data tracking during Bonsai workflows
- Support modular hardware configurations (ephys, miniscope, analog inputs, syringe control)
- Behavioral camera and event logging are included in all configurations by default

## Repository Structure

```
data_acquisition/
├── selector.py              # Main GUI for experiment selection and Bonsai launcher
├── setup_experiment.bat     # Quick launcher for selector.py (Windows)
├── bonsai_logging.py        # Logging GUI module for use with Bonsai workflows
├── paths.py                 # Path configuration and constants
├── data/
│   └── experiments.csv      # Experiment metadata and configurations
├── scripts/
│   ├── bonsai_base.bat                          # Base recording (camera + events)
│   ├── bonsai_ephys.bat                         # Ephys only
│   ├── bonsai_miniscope.bat                     # Miniscope only
│   ├── bonsai_analog.bat                        # Analog inputs only
│   ├── bonsai_syringe.bat                       # Syringe control only
│   ├── bonsai_ephys_miniscope.bat               # Ephys + Miniscope
│   ├── bonsai_ephys_analog.bat                  # Ephys + Analog
│   ├── bonsai_ephys_syringe.bat                 # Ephys + Syringe
│   ├── bonsai_miniscope_analog.bat              # Miniscope + Analog
│   ├── bonsai_miniscope_syringe.bat             # Miniscope + Syringe
│   ├── bonsai_ephys_miniscope_analog.bat        # Ephys + Miniscope + Analog
│   ├── bonsai_ephys_miniscope_syringe.bat       # Ephys + Miniscope + Syringe
│   ├── README.md                                # Scripts directory documentation
│   └── workflow_*.bonsai                        # Actual Bonsai workflows (create as needed)
├── README.md                # This file
└── LICENSE
```

## Getting Started

### Prerequisites

- Python 3.8+
- Conda or pip for package management
- Bonsai workflow engine
- ONIX hardware drivers

### Installation

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd data_acquisition
   ```

2. Create and activate the conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate data_acquisition
   ```

3. Verify dependencies are installed:
   ```bash
   pip list | grep -i "freesimplegui\|pandas"
   ```

## Usage

### Quick Start

The easiest way to launch the experiment selector is to double-click the batch file:

```bash
setup_experiment.bat
```

This will automatically activate the conda environment and launch the GUI.

Alternatively, from the command line in the data_acquisition directory:

```bash
python selector.py
```

### 1. Launching the Experiment Selector

The main interface for data acquisition is the experiment selector GUI.

**Available Modules:**
- **Core Recording Types:** Ephys, Miniscope (select any combination)
- **Optional Modules:** Analog Inputs, Syringe Use (select any combination)
- **Always Included:** Behavioral camera and event logging in all configurations

**Workflow:**
1. Select the desired recording modules (ephys, miniscope, or both)
2. Check any optional modules you need (analog inputs, syringe control)
3. Enter the experiment line number from `data/experiments.csv` and click "Confirm Line"
4. Click "Connect Hardware" to initialize hardware interfaces
5. Click "Launch Bonsai" to start the recording workflow

**Safety Features:**
- Failsafe prevents launching Bonsai without confirming an experiment line
- Error messages indicate missing .bat files or invalid configurations
- Visual indicator shows confirmed experiment status

### 2. Using Bonsai Logger in Workflows

The `bonsai_logging.py` module provides message logging capabilities within Bonsai workflows:

```python
from bonsai_logging import BonsaiLogger

# Create logger instance
logger = BonsaiLogger()
logger.start()

# Access message in your workflow
current_message = logger.state.message
if logger.state.submitted:
    print(f"User logged: {current_message}")
    logger.reset_submitted_flag()

# Stop when done
logger.stop()
```

**Features:**
- GUI textbox for entering messages
- Submit/Clear buttons
- Thread-safe operation (non-blocking)
- State tracking for submitted messages

### 3. Experiment Configuration

Experiments are defined in `data/experiments.csv`. Edit this file to add or modify experiment configurations that will be loaded by the selector.

## Currently Unimplemented / Placeholder Features

The following features are planned but not yet fully implemented:

1. **Heavy Data Processing Pipeline** (`selector.py:_process_experiment_row`)
   - Currently only provides basic data summaries
   - Placeholder for real data preprocessing and validation

2. **Background Data Processing** (`selector.py` after "Confirm Line")
   - Experiment configuration is validated but actual data processing pipeline is not triggered
   - Needs implementation of data ingestion, preprocessing, and storage

3. **Hardware Connection Interface** (`selector.py:"Connect Hardware"`)
   - Currently a placeholder that updates UI status
   - Needs ONIX driver integration and actual connection logic

4. **Real-time Data Monitoring**
   - GUI for displaying live recording status, data rates, and hardware health

5. **Data Export & Analysis Tools**
   - Tools for post-acquisition data export and preliminary analysis

6. **Error Handling & Logging**
   - Comprehensive logging to file for troubleshooting and auditing

## Development Notes

- The project uses **FreeSimpleGUI** (modern fork of PySimpleGUI) for GUI components
- Bonsai scripts are batch files that launch the Bonsai workflow engine
- **paths.py** centralizes path management for easy relocation of the project
- Experiment metadata is managed via CSV for easy version control and sharing

## Contributing

When adding features, please:
1. Update this README with new functionality
2. Use FreeSimpleGUI for any new UI components
3. Maintain centralized path management in `paths.py`
4. Add docstrings to new functions and classes

---

## Author

**Project Lead:** Luke M. (Melonakos Lab, BYU)


