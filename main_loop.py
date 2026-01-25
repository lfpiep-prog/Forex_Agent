import time
import sys

# Ensure imports work from current directory
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from execution.engine import TradingEngine
from core.logger import get_logger

# Setup structured logger
logger = get_logger("Scheduler")

# Create the Trading Engine (transitional: no DI yet, uses internal legacy logic)
engine = TradingEngine()

from datetime import datetime, timezone, timedelta

def get_seconds_until_next_hour():
    """Calculates seconds remaining until the next full hour (UTC)."""
    delta = timedelta(hours=1)
    now = datetime.now(timezone.utc)
    # Reset minutes, seconds, micros to zero and add one hour
    next_hour = (now + delta).replace(minute=0, second=0, microsecond=0)
    wait_seconds = (next_hour - now).total_seconds()
    return wait_seconds

if __name__ == "__main__":
    print("==============================================")
    print("   Forex Agent - Continuous Execution Mode    ")
    print("==============================================")
    print("Press Ctrl+C to stop safely.\n")
    
    status_printed = False
    
    try:
        # Initial check to see if we should run immediately? 
        # Strategy usually requires closed candles (H1), so waiting for the hour mark is safer
        # to ensure we have the full previous hour's data.
        
        while True:
            wait_sec = get_seconds_until_next_hour()
            
            # Formatting for display
            wait_mins = int(wait_sec / 60)
            next_run_time = datetime.now(timezone.utc) + timedelta(seconds=wait_sec)
            
            logger.info(f"Waiting {wait_mins} minutes until next check at {next_run_time.strftime('%H:%M:%S')} UTC...")
            
            # Sleep until the hour mark + buffer
            # We add 5 seconds buffer to ensure data providers have closed the candle
            time.sleep(wait_sec + 5) 
            
            logger.info("--- STARTING HOURLY CHECK ---")
            print(f">>> Executing Pipeline at {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            
            try:
                engine.run_cycle()
                logger.info("--- HOURLY CHECK COMPLETED ---")
            except Exception as e:
                logger.error(f"Critical Error during pipeline execution: {e}", exc_info=True)
                
            # Sleep a bit to prevent double-triggering if the loop wraps fast
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted execution. Exiting...")
        sys.exit(0)
