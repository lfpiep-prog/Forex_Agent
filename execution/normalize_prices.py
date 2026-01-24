import argparse
import pandas as pd
from pathlib import Path

REQUIRED_COLUMNS = ['timestamp', 'open', 'high', 'low', 'close']
OPTIONAL_COLUMNS = ['volume']

def normalize_file(input_path, output_dir):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return False
        
    try:
        # Read CSV - assume headers exist for now based on Mock format
        df = pd.read_csv(input_path)
        
        # Normalize Column Names (simple mapping for now, can be expanded)
        # Expecting generic names or standard names
        df.columns = [c.lower() for c in df.columns]
        
        # Rename 'time' to 'timestamp' if present
        if 'time' in df.columns:
            df.rename(columns={'time': 'timestamp'}, inplace=True)
            
        # Ensure timestamp is datetime and UTC
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Ensure 'symbol' exists. If not valid in file, we might need to infer or pass it.
        # For this MVP, we will extract symbol from filename if possible or just rely on structure.
        # But per contract, 'symbol' column is required.
        # If input doesn't have symbol, we'll try to guess from filename (e.g. EURUSD_...)
        if 'symbol' not in df.columns:
            # naive extraction: assume filename starts with symbol
            filename_parts = input_path.name.split('_')
            if len(filename_parts) > 0:
                 df['symbol'] = filename_parts[0]
            else:
                 df['symbol'] = 'UNKNOWN'
        
        # Ensure standard columns exist
        for col in REQUIRED_COLUMNS:
            if col not in df.columns:
                print(f"Error: Missing required column {col} in {input_path}")
                return False
                
        # Fill missing volume with 0
        if 'volume' not in df.columns:
            df['volume'] = 0.0
        else:
            df['volume'] = df['volume'].fillna(0)
            
        # Select and reorder columns
        cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close', 'volume']
        df = df[cols]
        
        # Type casting
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        
        # Sort by timestamp
        df.sort_values('timestamp', inplace=True)
        
        # Output logic
        # We need to save to data/processed/{symbol}/{granularity}.parquet
        # For MOCK, we treat as M1.
        symbol = df['symbol'].iloc[0]
        symbol_dir = output_dir / symbol
        symbol_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = symbol_dir / "M1.csv"
        print(f"Saving normalized data to {output_file}...")
        df.to_csv(output_file, index=False)
        return True
        
    except Exception as e:
        print(f"Error normalizing {input_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Normalize price data.")
    parser.add_argument("--input", required=True, help="Path to raw input file")
    
    args = parser.parse_args()
    
    processed_dir = Path("data/processed")
    
    success = normalize_file(args.input, processed_dir)
    
    if success:
        print("Normalization completed successfully.")
    else:
        print("Normalization failed.")
        exit(1)

if __name__ == "__main__":
    main()
