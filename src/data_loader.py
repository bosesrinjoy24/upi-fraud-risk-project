import pandas as pd
from pathlib import Path

# Dynamically resolve project root
ROOT_DIR = Path(__file__).resolve().parent.parent

def load_data():
    path = ROOT_DIR / "data" / "UPI_FRAUD_100K.csv"
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}. Please place UPI_FRAUD_100K.csv in the data/ folder.")
    df = pd.read_csv(path)
    return df