"""
Forex Agent - Main Entry Point
==============================
Continuous execution mode for production trading.

Usage:
    python execution/main_loop.py           # Normal mode (hourly loop)
    python execution/main_loop.py --smoke   # Smoke test (single cycle, exit)
"""

import time
import sys
import os
import argparse

# Ensure imports work from current directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from execution.engine import TradingEngine
from execution.core.logger import get_logger

# Setup structured logger
logger = get_logger("Scheduler")

from execution.health_check import run_health_check
from execution.daily_summary import run_daily_summary

from datetime import datetime, timezone, timedelta


def get_seconds_until_next_hour():
    """Calculates seconds remaining until the next full hour (UTC)."""
    delta = timedelta(hours=1)
    now = datetime.now(timezone.utc)
    next_hour = (now + delta).replace(minute=0, second=0, microsecond=0)
    wait_seconds = (next_hour - now).total_seconds()
    return wait_seconds


def run_smoke_test():
    """
    Smoke test mode: Run ONE cycle immediately and exit.
    
    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    print("=" * 50)
    print("   Forex Agent - SMOKE TEST MODE")
    print("=" * 50)
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC\n")
    
    try:
        # Step 1: Health Check
        logger.info("[Smoke] Step 1/3: Health Check...")
        result = run_health_check(send_notification=False)
        if result.get("overall_status") == "DOWN":
            logger.error("[Smoke] Health check FAILED - system is DOWN")
            return 1
        logger.info(f"[Smoke] Health: {result.get('overall_status')}")
        
        # Step 2: Engine Initialization
        logger.info("[Smoke] Step 2/3: Initializing Trading Engine...")
        engine = TradingEngine()
        logger.info("[Smoke] Engine initialized successfully")
        
        # Step 3: Run One Cycle (no actual trading in smoke mode)
        logger.info("[Smoke] Step 3/3: Running Pipeline Cycle...")
        engine.run_cycle()
        logger.info("[Smoke] Pipeline cycle completed")
        
        print("\n" + "=" * 50)
        print("   ✅ SMOKE TEST PASSED")
        print("=" * 50)
        return 0
        
    except Exception as e:
        logger.error(f"[Smoke] FAILED: {e}", exc_info=True)
        print("\n" + "=" * 50)
        print(f"   ❌ SMOKE TEST FAILED: {e}")
        print("=" * 50)
        return 1


def run_continuous():
    """Normal continuous execution mode - runs hourly cycles."""
    print("=" * 50)
    print("   Forex Agent - Continuous Execution Mode")
    print("=" * 50)
    print("Press Ctrl+C to stop safely.\n")
    
    # Create the Trading Engine
    engine = TradingEngine()
    
    try:
        # --- Startup Health Check ---
        try:
            logger.info("Running Startup Health Check...")
            run_health_check()
        except Exception as e:
            logger.error(f"Startup Health Check Failed: {e}")
        
        while True:
            wait_sec = get_seconds_until_next_hour()
            
            # Formatting for display
            wait_mins = int(wait_sec / 60)
            next_run_time = datetime.now(timezone.utc) + timedelta(seconds=wait_sec)
            
            logger.info(f"Waiting {wait_mins} minutes until next check at {next_run_time.strftime('%H:%M:%S')} UTC...")
            
            # Sleep until the hour mark + buffer
            time.sleep(wait_sec + 5) 
            
            logger.info("--- STARTING HOURLY CHECK ---")
            print(f">>> Executing Pipeline at {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")
            
            try:
                engine.run_cycle()
                
                # --- Scheduled Tasks ---
                now_check = datetime.now(timezone.utc)
                
                # Health Check: Every 5 Hours
                if now_check.hour % 5 == 0:
                    logger.info(f"Running Scheduled Health Check (Hour {now_check.hour})...")
                    try:
                        run_health_check()
                    except Exception as e:
                        logger.error(f"Scheduled Health Check Failed: {e}")

                # Daily Summary: At 22:00 UTC
                if now_check.hour == 22:
                    logger.info("Running Daily Summary at 22:00 UTC...")
                    try:
                        run_daily_summary()
                    except Exception as e:
                        logger.error(f"Daily Summary Failed: {e}")

                logger.info("--- HOURLY CHECK COMPLETED ---")
            except Exception as e:
                logger.error(f"Critical Error during pipeline execution: {e}", exc_info=True)
                
            # Sleep to prevent double-triggering
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted execution. Exiting...")
        sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Forex Agent Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python execution/main_loop.py           # Normal production mode
  python execution/main_loop.py --smoke   # Quick validation test
        """
    )
    parser.add_argument(
        "--smoke", 
        action="store_true",
        help="Run smoke test (single cycle) and exit with status code"
    )
    
    args = parser.parse_args()
    
    # Check for SMOKE_MODE env var as fallback (for Docker)
    smoke_from_env = os.getenv("SMOKE_MODE", "false").lower() == "true"
    
    if args.smoke or smoke_from_env:
        exit_code = run_smoke_test()
        sys.exit(exit_code)
    else:
        run_continuous()

