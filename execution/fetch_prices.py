import argparse
import os
import shutil
import datetime
from pathlib import Path

def fetch_mock(symbol, start_date, end_date, output_dir):
    """
    Simulates fetching data by copying the sample.csv to the output directory.
    In a real scenario, this would filter the CSV by date.
    """
    mock_source = Path(".tmp/sample.csv")
    if not mock_source.exists():
        print(f"Error: Mock source file {mock_source} not found.")
        return False
    
    # Create a unique filename based on symbol and timestamp to avoid overwrites
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    target_file = output_dir / f"{symbol}_MOCK_{timestamp_str}.csv"
    
    print(f"Copying mock data from {mock_source} to {target_file}...")
    shutil.copy(mock_source, target_file)
    return True

def main():
    parser = argparse.ArgumentParser(description="Fetch historical price data.")
    parser.add_argument("--symbol", required=True, help="Trading Pair (e.g. EURUSD)")
    parser.add_argument("--start_date", help="Start date YYYY-MM-DD")
    parser.add_argument("--end_date", help="End date YYYY-MM-DD")
    parser.add_argument("--provider", default="MOCK", help="Data provider (default: MOCK)")
    
    args = parser.parse_args()
    
    # Ensure data/raw exists
    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    if args.provider.upper() == "MOCK":
        success = fetch_mock(args.symbol, args.start_date, args.end_date, raw_dir)
    elif args.provider.upper() == "TWELVEDATA":
        try:
            from execution.data_sources.twelvedata_source import TwelveDataSource
            
            s_date = args.start_date if args.start_date else (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
            e_date = args.end_date if args.end_date else datetime.datetime.now().strftime("%Y-%m-%d")
            
            source = TwelveDataSource()
            print(f"Fetching TwelveData for {args.symbol} from {s_date} to {e_date}...")
            df = source.fetch_candles(args.symbol, s_date, e_date)
            
            if not df.empty:
                timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                target_file = raw_dir / f"{args.symbol}_TWELVEDATA_{timestamp_str}.csv"
                df.to_csv(target_file, index=False)
                print(f"Saved {len(df)} candles to {target_file}")
                success = True
            else:
                print("No data returned from TwelveData.")
                success = False
        except Exception as e:
            print(f"TwelveData fetch failed: {e}")
            success = False
    else:
        print(f"Error: Provider {args.provider} not implemented yet.")
        success = False
        
    if success:
        print("Fetch completed successfully.")
    else:
        print("Fetch failed.")
        exit(1)

if __name__ == "__main__":
    main()
