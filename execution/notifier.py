import os
import requests
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ForexPlatform")

class DiscordNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        self.enabled = bool(self.webhook_url)
        if not self.enabled:
            logger.warning("DiscordNotifier disabled: No DISCORD_WEBHOOK_URL found.")

    def send_message(self, content: str, username: str = "Forex Agent"):
        """Sends a simple text message to Discord."""
        if not self.enabled:
            return

        data = {
            "content": content,
            "username": username
        }
        self._post(data)

    def send_trade_alert(self, signal: Dict[str, Any], order_intent: Any, result: Any):
        """Sends a rich formatted embed for a trade execution."""
        if not self.enabled:
            return

        status_emoji = "✅" if result.status in ["FILLED", "SUBMITTED"] else "❌"
        color = 5763719 if result.status in ["FILLED", "SUBMITTED"] else 15548997 # Green / Red

        embed = {
            "title": f"{status_emoji} COMPLETED: {signal['direction']} {signal['symbol']}",
            "color": color,
            "fields": [
                {"name": "Status", "value": result.status, "inline": True},
                {"name": "Size", "value": f"{order_intent.quantity}", "inline": True},
                {"name": "Entry Price", "value": f"{signal.get('entry_price', 'N/A')}", "inline": True},
                {"name": "Stop Loss", "value": f"{signal.get('stop_loss', 'N/A')}", "inline": True},
                {"name": "Take Profit", "value": f"{signal.get('take_profit', 'N/A')}", "inline": True},
                {"name": "Rationale", "value": signal.get('rationale', 'No rationale provided')[:1000], "inline": False}
            ],
            "footer": {"text": f"Order ID: {result.order_id if hasattr(result, 'order_id') else 'N/A'}"},
            "timestamp": signal.get('timestamp').isoformat() if hasattr(signal.get('timestamp'), 'isoformat') else None
        }

        data = {
            "username": "Forex Execution",
            "embeds": [embed]
        }
        self._post(data)

    def send_error(self, message: str):
        """Sends an error alert."""
        if not self.enabled:
            return

        embed = {
            "title": "🚨 CRITICAL ERROR",
            "description": message,
            "color": 15548997, # Red
        }
        
        data = {
            "username": "Forex Alert",
            "embeds": [embed]
        }
        self._post(data)

    def send_close_alert(self, trade: Dict[str, Any], pnl: float):
        """Sends a notification when a position is closed."""
        if not self.enabled:
            return

        is_profit = pnl >= 0
        status_emoji = "💰" if is_profit else "📉"
        color = 5763719 if is_profit else 15548997  # Green / Red
        pnl_str = f"+{pnl:.2f}" if is_profit else f"{pnl:.2f}"

        embed = {
            "title": f"{status_emoji} CLOSED: {trade.get('direction', 'N/A')} {trade.get('symbol', 'N/A')}",
            "color": color,
            "fields": [
                {"name": "Entry", "value": f"{trade.get('entry_price', 'N/A')}", "inline": True},
                {"name": "Exit", "value": f"{trade.get('exit_price', 'N/A')}", "inline": True},
                {"name": "PnL", "value": pnl_str, "inline": True},
                {"name": "Size", "value": f"{trade.get('quantity', 'N/A')}", "inline": True},
            ],
            "footer": {"text": f"Order ID: {trade.get('broker_order_id', 'N/A')}"},
        }

        data = {
            "username": "Forex Execution",
            "embeds": [embed]
        }
        self._post(data)

    def send_daily_summary(self, summary: Dict[str, Any]):
        """Sends an end-of-day summary report."""
        if not self.enabled:
            return

        total_pnl = summary.get("total_pnl", 0)
        is_profit = total_pnl >= 0
        color = 5763719 if is_profit else 15548997
        pnl_emoji = "📈" if is_profit else "📉"
        pnl_str = f"+{total_pnl:.2f}" if is_profit else f"{total_pnl:.2f}"

        embed = {
            "title": f"📊 Daily Summary - {summary.get('date', 'Today')}",
            "color": color,
            "fields": [
                {"name": "Total Trades", "value": str(summary.get("total_trades", 0)), "inline": True},
                {"name": "Wins", "value": str(summary.get("wins", 0)), "inline": True},
                {"name": "Losses", "value": str(summary.get("losses", 0)), "inline": True},
                {"name": f"{pnl_emoji} PnL", "value": pnl_str, "inline": True},
                {"name": "Equity", "value": f"{summary.get('equity', 'N/A')}", "inline": True},
                {"name": "Win Rate", "value": f"{summary.get('win_rate', 0):.1f}%", "inline": True},
            ],
            "footer": {"text": "End of Day Report"},
        }

        data = {
            "username": "Forex Daily",
            "embeds": [embed]
        }
        self._post(data)

    def _post(self, data: Dict[str, Any]):
        try:
            response = requests.post(self.webhook_url, json=data, timeout=10)
            response.raise_for_status()
        except requests.Timeout:
            logger.warning("Discord notification timed out (10s)")
        except requests.RequestException as e:
            logger.error(f"Discord notification failed: {e}")

