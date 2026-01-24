import argparse
import pandas as pd
from pathlib import Path

def validate_file(input_path):
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist.")
        return False
        
    try:
        df = pd.read_csv(input_path)
        
        # Ensure timestamp is datetime (CSV loses this info)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        
        # Check 1: Required columns
        required_cols = ['timestamp', 'symbol', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in df.columns:
                print(f"FAIL: Missing column {col}")
                return False
                
        # Check 2: No NaNs in prices
        price_cols = ['open', 'high', 'low', 'close']
        if df[price_cols].isnull().any().any():
            print("FAIL: NaN values found in price columns")
            return False
            
        # Check 3: Timestamps are sorted
        if not df['timestamp'].is_monotonic_increasing:
            print("FAIL: Timestamps are not strictly increasing")
            return False
            
        # Check 4: No duplicate timestamps
        if df['timestamp'].duplicated().any():
            print("FAIL: Duplicate timestamps found")
            return False
            
        # Check 5: Logical price consistency (Low <= Open/Close <= High)
        # Allow small floating point tolerance if needed, but for now strict
        if not (
            (df['low'] <= df['open']).all() and
            (df['low'] <= df['close']).all() and
            (df['low'] <= df['high']).all() and
            (df['high'] >= df['open']).all() and
            (df['high'] >= df['close']).all()
        ):
             print("FAIL: Price inconsistency found (e.g. Low > High)")
             # Identify rows
             # invalid = df[~((df['low'] <= df['high']))]
             # print(invalid.head())
             return False

        print(f"PASS: {input_path} passed all checks. Rows: {len(df)}")
        return True
        
    except Exception as e:
        print(f"Error validating {input_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Validate normalized data.")
    parser.add_argument("--input", required=True, help="Path to normalized file")
    
    args = parser.parse_args()
    
    success = validate_file(args.input)
    
    if success:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
