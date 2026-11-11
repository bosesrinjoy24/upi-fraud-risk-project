import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    # Work on a copy to prevent modifying the original dataframe
    df = df.copy()
    
    # Parse datetime using strict format
    df['datetime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'], 
        format='%d/%m/%y %I:%M:%S %p'
    )
    
    # Transaction-level features
    df['hour'] = df['datetime'].dt.hour
    df['day_of_week'] = df['datetime'].dt.day_of_week
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Log transform amount to handle skew
    df['amount_log'] = np.log1p(df['amount'])
    
    return df

def get_feature_columns():
    numeric = [
        'Transaction_Frequency', 'Transaction_Amount_Deviation', 
        'Days_Since_Last_Transaction', 'amount_log', 
        'hour', 'day_of_week', 'is_weekend'
    ]
    categorical = [
        'Transaction_Type', 'Payment_Gateway', 'Merchant_Category', 
        'Transaction_Channel', 'Device_OS'
    ]
    return numeric, categorical