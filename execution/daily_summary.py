"""
Daily Summary Script
Sends an end-of-day summary to Discord.

Run manually: python -m execution.daily_summary
Or via cron: 0 22 * * * cd /path/to/project && python -m execution.daily_summary
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from execution.core.database import engine
from execution.core.models import TradeResult
from execution.notifier import DiscordNotifier
from execution.account import AccountManager


def get_todays_trades(db: Session) -> list:
    """Fetches all trades from today (UTC)."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    trades = db.query(TradeResult).filter(
        TradeResult.timestamp >= today_start
    ).all()
    
    return trades


def calculate_summary(trades: list, equity: float) -> dict:
    """Calculates summary statistics from trades."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    if not trades:
        return {
            "date": today,
            "total_trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0.0,
            "equity": equity,
            "win_rate": 0.0
        }
    
    wins = sum(1 for t in trades if t.pnl and t.pnl > 0)
    losses = sum(1 for t in trades if t.pnl and t.pnl < 0)
    total_pnl = sum(t.pnl or 0 for t in trades)
    total_closed = wins + losses
    win_rate = (wins / total_closed * 100) if total_closed > 0 else 0.0
    
    return {
        "date": today,
        "total_trades": len(trades),
        "wins": wins,
        "losses": losses,
        "total_pnl": total_pnl,
        "equity": equity,
        "win_rate": win_rate
    }


def run_daily_summary():
    """Main function to generate and send daily summary."""
    print(f"[{datetime.now()}] Running Daily Summary...")
    
    # Get current equity
    account = AccountManager()
    snapshot = account.get_snapshot()
    equity = snapshot.get("equity", 10000)
    
    # Get today's trades
    db = Session(bind=engine)
    try:
        trades = get_todays_trades(db)
        summary = calculate_summary(trades, equity)
        
        print(f"Summary: {summary}")
        
        # Send to Discord
        notifier = DiscordNotifier()
        notifier.send_daily_summary(summary)
        
        print(f"[{datetime.now()}] Daily Summary sent to Discord.")
    finally:
        db.close()


if __name__ == "__main__":
    run_daily_summary()
