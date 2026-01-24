import time
import datetime
import logging
import sys
import os

# Ensure imports work from current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from execution.run_cycle import run_pipeline

# Setup simple console logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - LOOP - %(message)s')
logger = logging.getLogger("OvernightLoop")

def get_seconds_until_next_hour():
    """Calculates seconds remaining until the next full hour."""
    delta = datetime.timedelta(hours=1)
    now = datetime.datetime.now()
    # Reset minutes, seconds, micros to zero and add one hour
    next_hour = (now + delta).replace(minute=0, second=0, microsecond=0)
    wait_seconds = (next_hour - now).total_seconds()
    return wait_seconds

if __name__ == "__main__":
    print("==============================================")
    print("   Forex Agent - OVERNIGHT LOOP (USDJPY)      ")
    print("==============================================")
    print("Provider: Twelve Data (800 calls/day limit safe)")
    print("Strategy: baseline_sma_cross")
    print("Timeframe: H1")
    print("Press Ctrl+C to stop safely.\n")
    
    try:
        # Run ONCE immediately to check system (User wants to test "bis morgen früh", implied start now?)
        # But usually hourly strategy waits for closed candle.
        # Let's ask user? Or just wait for next hour? 
        # Typically "run loop" implies waiting for the schedule.
        # But let's run a "Sanity Check" (Verification) first?
        # No, risk of taking trades mid-candle. 
        # Better: Wait for next hour.
        
        while True:
            wait_sec = get_seconds_until_next_hour()
            wait_mins = int(wait_sec / 60)
            next_run_time = datetime.datetime.now() + datetime.timedelta(seconds=wait_sec)
            
            logger.info(f"Sleeping {wait_mins} min until {next_run_time.strftime('%H:%M:%S')}...")
            
            # Sleep
            time.sleep(wait_sec + 2) # +2s buffer
            
            logger.info("--- WAKE UP: STARTING CYCLE ---")
            try:
                run_pipeline()
                logger.info("--- CYCLE COMPLETED ---")
            except Exception as e:
                logger.error(f"Cycle failed: {e}")
                
            # Sleep a bit to clear the minute matching logic if any
            time.sleep(10)

    except KeyboardInterrupt:
        print("\n[STOPPED] Exiting...")
        sys.exit(0)
