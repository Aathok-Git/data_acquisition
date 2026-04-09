# data_acquisition

A data acquisition launcher for the Melonakos Lab at BYU. This repository provides a GUI-based selector to configure and launch Bonsai workflows for ONIX experiments, with support for ephys, miniscope, analog inputs, and syringe pump control.

## Overview

- `selector.py` is the main GUI application for selecting experiment modules and launching Bonsai scripts.
- `paths.py` centralizes path configuration, including the experiment metadata CSV and the output results directory.
- `data/experiments.csv` stores the experiment metadata used by the selector.
- `scripts/` contains batch launchers for each supported module combination.
- `setup_experiment.bat` is a Windows helper script that activates the conda environment and starts the selector GUI.

## Repository Structure

```
data_acquisition/
├── selector.py
├── setup_experiment.bat
├── paths.py
├── environment.yml
├── data/
│   └── experiments.csv
├── scripts/
│   ├── bonsai_analog.bat
│   ├── bonsai_analog_syringe.bat
│   ├── bonsai_base.bat
│   ├── bonsai_ephys.bat
│   ├── bonsai_ephys_analog.bat
│   ├── bonsai_ephys_analog_syringe.bat
│   ├── bonsai_ephys_miniscope.bat
│   ├── bonsai_ephys_miniscope_analog.bat
│   ├── bonsai_ephys_miniscope_analog_syringe.bat
│   ├── bonsai_ephys_miniscope_syringe.bat
│   ├── bonsai_ephys_syringe.bat
│   ├── bonsai_miniscope.bat
│   ├── bonsai_miniscope_analog.bat
│   ├── bonsai_miniscope_analog_syringe.bat
│   ├── bonsai_miniscope_syringe.bat
│   └── bonsai_syringe.bat
├── bonsai/
│   ├── bonsai_base.bonsai
│   ├── bonsai_base.layout
│   ├── DraftMasterWorkflow.bonsai
│   └── ...
├── README.md
└── LICENSE
```

## Prerequisites

- Conda (Miniconda or Anaconda)
- Python 3.10
- Bonsai installed and available on the system PATH
- Windows is the primary supported platform for the provided `.bat` launchers

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd data_acquisition
   ```

2. Create the conda environment from `environment.yml`:

   ```bash
   conda env create -f environment.yml
   ```

3. Activate the environment:

   ```bash
   conda activate data_acquisition
   ```

4. Confirm required Python packages are installed:

   ```bash
   conda list | findstr /R "freesimplegui pandas"
   ```

5. Verify Bonsai is accessible from the command line:

   ```bash
   bonsai --version
   ```

> If `conda` is not available, install Python 3.10 and then run:
>
> ```bash
> pip install freesimplegui==5.2.0.post1 pandas
> ```

## Configuration

### `paths.py`

This file defines project paths used by the selector:

- `EXPERIMENTS` points to `data/experiments.csv`
- `OUTPUT_DIR` points to `data/experiment_results`

Modify these values only if you move the repository or want to use a different output directory.

### `data/experiments.csv`

This CSV file holds experiment metadata and is required for the selector to confirm a run. Each row should represent one experiment configuration.

## Usage

### Windows Quick Start

Run the helper batch script:

```bash
setup_experiment.bat
```

This script changes to the project directory, activates the `data_acquisition` conda environment, and launches `selector.py`.

### Manual Start

From the activated conda environment, start the selector directly:

```bash
python selector.py
```

### Using the Selector GUI

1. Choose core recording modules (selecting none is an option):
   - `Ephys`
   - `Miniscope`

2. Choose optional modules:
   - `Analog Inputs`
   - `Syringe Use`

3. Enter an experiment line number from `data/experiments.csv` and click `Confirm Line`.
4. The GUI will display experiment details and confirm whether syringe control is available.
5. Click the folder icon to open the configured output directory.
6. Click `Launch Bonsai` to start the selected Bonsai workflow.

### Output Folder

The folder icon in the GUI opens the directory defined by `OUTPUT_DIR` in `paths.py`, usually:

```text
data/experiment_results
```

This directory is created automatically if it does not already exist.

## Scripts and Workflow Launching

`selector.py` chooses the correct batch file in `scripts/` based on the selected modules. The naming pattern is:

- `bonsai_base.bat`
- `bonsai_ephys.bat`
- `bonsai_miniscope.bat`
- `bonsai_analog.bat`
- `bonsai_syringe.bat`
- and combinations like `bonsai_ephys_miniscope_analog.bat`

Each script launches Bonsai with the selected workflow and passes the output directory and rat name as arguments.

## Notes

- The GUI prevents Bonsai launch until an experiment line is confirmed.
- The selector supports syringe pump setup and will attempt to configure it when `Syringe Use` is selected.
- The project currently uses `FreeSimpleGUI` for the interface and assumes Bonsai is present on the host machine.

## Contributing

If you add new features or hardware support:

1. Update `README.md` with the new behavior.
2. Update `paths.py` if you add new path configuration.
3. Add or update a script in `scripts/` for the new workflow.
4. Keep GUI logic in `selector.py` clean and documented.

---
## Author

**Project Lead:** Luke M. (Melonakos Lab, BYU)


## License

This project is licensed under the terms in `LICENSE`.


