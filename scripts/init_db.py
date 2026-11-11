import sqlite3
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path so we can import src
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.data_loader import ROOT_DIR

def init_db():
    csv_path = ROOT_DIR / "data" / "UPI_FRAUD_100K.csv"
    db_path = ROOT_DIR / "data" / "fraud.db"
    
    if not csv_path.exists():
        print(f"Error: Could not find dataset at {csv_path}")
        return

    print("Loading CSV...")
    df = pd.read_csv(csv_path)
    
    print("Connecting to SQLite...")
    conn = sqlite3.connect(db_path)
    
    print("Writing to SQLite table 'transactions'...")
    # This automatically creates the table and inserts the data
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Success! Database created at {db_path}")
    print("You can now run the SQL scripts in DB Browser for SQLite.")

if __name__ == "__main__":
    init_db()