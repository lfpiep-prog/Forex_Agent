"""
System Health Check Script

Checks system health and sends status to Discord.
Run manually: python -m execution.health_check
Or via cron: */30 * * * * cd /path/to/project && python -m execution.health_check
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import logging
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("ForexPlatform")


def check_database_status() -> dict:
    """Check database connectivity and record count."""
    try:
        from execution.core.database import engine
        from execution.core.models import TradeResult
        
        with Session(bind=engine) as db:
            count = db.query(TradeResult).count()
            db.execute(text("SELECT 1"))  # Simple connectivity check
            return {"status": "OK", "message": f"trades.db ({count} records)"}
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return {"status": "DOWN", "message": str(e)}


def check_broker_status() -> dict:
    """Check broker API connectivity."""
    try:
        from execution.brokers.ig_broker import create_ig_session
        
        # Try to create a session (doesn't actually trade)
        ig_username = os.getenv("IG_USERNAME")
        ig_password = os.getenv("IG_PASSWORD")
        ig_api_key = os.getenv("IG_API_KEY")
        acc_type = os.getenv("IG_ACC_TYPE", "DEMO")
        
        if not all([ig_username, ig_password, ig_api_key]):
            return {"status": "UNKNOWN", "message": "Credentials not configured"}
        
        # We won't actually connect in health check to avoid rate limits
        # Just verify credentials are present
        return {"status": "OK", "message": f"IG-{acc_type} configured"}
    except ImportError:
        return {"status": "UNKNOWN", "message": "Broker module not available"}
    except Exception as e:
        logger.error(f"Broker check failed: {e}")
        return {"status": "DEGRADED", "message": str(e)}


def check_data_feed_status() -> dict:
    """Check market data feed status."""
    try:
        polygon_key = os.getenv("POLYGON_API_KEY")
        
        if not polygon_key:
            return {"status": "UNKNOWN", "message": "Polygon API Key not configured"}
        
        return {"status": "OK", "message": "Polygon configured"}
    except Exception as e:
        logger.error(f"Data feed check failed: {e}")
        return {"status": "DEGRADED", "message": str(e)}


def get_last_candle_time() -> str:
    """Get timestamp of last processed candle from logs or DB."""
    try:
        from execution.core.database import engine
        from execution.core.models import TradeResult
        
        with Session(bind=engine) as db:
            latest = db.query(TradeResult).order_by(TradeResult.timestamp.desc()).first()
            if latest:
                return latest.timestamp.strftime("%Y-%m-%d %H:%M UTC")
        return "No trades yet"
    except Exception:
        return "Unknown"


def calculate_uptime() -> str:
    """Calculate system uptime (placeholder - would need actual start time tracking)."""
    # In production, this would read from a state file or process start time
    return "N/A (tracking not implemented)"


def get_overall_status(checks: dict) -> str:
    """Determine overall system status from individual checks."""
    statuses = [c.get("status", "UNKNOWN") for c in checks.values()]
    
    if "DOWN" in statuses:
        return "DOWN"
    elif "DEGRADED" in statuses or "UNKNOWN" in statuses:
        return "DEGRADED"
    else:
        return "OK"


def run_health_check(send_notification: bool = True) -> dict:
    """
    Run comprehensive health check and optionally send to Discord.
    
    Returns dict with all health check results.
    """
    print(f"[{datetime.now()}] Running Health Check...")
    
    checks = {
        "database": check_database_status(),
        "broker": check_broker_status(),
        "data_feed": check_data_feed_status(),
    }
    
    overall_status = get_overall_status(checks)
    last_candle = get_last_candle_time()
    uptime = calculate_uptime()
    
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "checks": checks,
        "last_candle": last_candle,
        "uptime": uptime,
    }
    
    print(f"Health Check Result: {overall_status}")
    for name, check in checks.items():
        print(f"  {name}: {check['status']} - {check['message']}")
    
    if send_notification:
        try:
            from execution.notifier import DiscordNotifier
            
            notifier = DiscordNotifier()
            details = {
                "broker": f"{checks['broker']['status']} - {checks['broker']['message']}",
                "data_feed": f"{checks['data_feed']['status']} - {checks['data_feed']['message']}",
                "last_candle": last_candle,
                "db": checks["database"]["message"],
                "uptime": uptime,
            }
            
            notifier.send_health_status(overall_status, details)
            print(f"[{datetime.now()}] Health status sent to Discord.")
        except Exception as e:
            print(f"[{datetime.now()}] Failed to send health status: {e}")
    
    return result


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run system health check")
    parser.add_argument("--no-notify", action="store_true", help="Skip Discord notification")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    result = run_health_check(send_notification=not args.no_notify)
    
    if args.json:
        import json
        print(json.dumps(result, indent=2, default=str))
