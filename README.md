# data_acquisition

A data acquisition launcher for the Melonakos Lab at BYU. This project provides a GUI selector for confirming experiment metadata from a CSV and launching the appropriate Bonsai workflow for ONIX experiments, including ephys, miniscope, analog inputs, and syringe pump control.

## Overview

- `selector.py` is the main GUI application for selecting experiment modules and launching Bonsai scripts.
- `paths.py` centralizes path configuration, including the experiment metadata CSV and output directory.
- `data/experiments.csv` stores the experiment metadata used by the selector.
- `scripts/` contains batch launchers for each supported module combination.
- `setup_experiment.bat` starts the selector in the correct conda environment.

## Current project behavior

The selector is currently configured around a CSV-driven experiment workflow:

- the user picks the module combination in the GUI
- the user confirms a row from the experiments CSV
- the GUI reads the row metadata and selects the matching launch script
- ephys channel configuration is read from the CSV field `Ephys Channels`
- if the selected module includes ephys, the validated channel list is passed to the batch file as the variable `EphysChannels`
- if ephys is not selected, the channel list is ignored

This means all channel configuration lives in the experiment CSV rather than in a GUI input field.

## Repository structure

```text
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
├── LICENSE
└── todo.md
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

4. Verify the required packages are installed:

   ```bash
   conda list | findstr /R "freesimplegui pandas"
   ```

5. Verify Bonsai is available from the shell:

   ```bash
   bonsai --version
   ```

## Configuration

### `paths.py`

This file defines project paths used by the selector:

- `EXPERIMENTS` points to `data/experiments.csv`
- `OUTPUT_DIR` points to `data/experiment_results`

### `data/experiments.csv`

This CSV is the source of experiment metadata. Each row should represent one experiment configuration.

For ephys workflows, include an `Ephys Channels` column. The selector reads and validates it. If a row is missing that column or the value is blank, it falls back to:

```text
0,1,2,3,4,5,6,7
```

Valid values are integer channel numbers from 0 through 31, separated by commas. Example:

```text
0,1,2,3,4,5,6,7
2,5,8,15
```

## Usage

### Windows quick start

Run:

```bash
setup_experiment.bat
```

This activates the project conda environment and launches `selector.py`.

### Manual start

```bash
python selector.py
```

### Using the selector GUI

1. Choose the core recording modules (selecting none is an option):
   - `Ephys`
   - `Miniscope`

2. Choose optional modules:
   - `Analog Inputs`
   - `Syringe Use`

3. Enter a line number from `data/experiments.csv` and click `Confirm Line`.
4. The GUI displays the confirmed experiment row and infusion metadata.
5. Click the folder icon to open the output directory.
6. Click `Launch Bonsai` to start the selected workflow.

### Output folder

The GUI opens the directory defined by `OUTPUT_DIR` in `paths.py`, usually:

```text
data/experiment_results
```

## Script and workflow launching

`selector.py` chooses the correct batch file in `scripts/` based on the selected modules. The naming pattern is:

- `bonsai_base.bat`
- `bonsai_ephys.bat`
- `bonsai_miniscope.bat`
- `bonsai_analog.bat`
- `bonsai_syringe.bat`
- and combinations such as `bonsai_ephys_miniscope_analog.bat`

Each script launches Bonsai using the selected workflow and passes the output directory, rat name, and, when applicable, the ephys channel string as `EphysChannels`.

## Notes

- The GUI prevents launch until a valid experiment row is confirmed.
- Syringe configuration is attempted only when the `Syringe Use` option is selected and the experiment row includes valid infusion data.
- The channel list is CSV-controlled; there is no GUI field for channel entry.

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


