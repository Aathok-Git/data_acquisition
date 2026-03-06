from pathlib import Path

# Base directory for the project
BASE_DIR = Path(__file__).parent.parent

# Data acquisition directories
DATA_DIR = BASE_DIR / "data"
EXPERIMENTS = DATA_DIR / "experiments.csv"
