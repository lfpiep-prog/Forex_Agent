"""
Discord Notifier Module - Multi-Channel Support

Sends notifications to different Discord channels based on event type.
Supports fallback to main webhook if channel-specific webhooks are not configured.
"""

import os
import requests
import logging
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ForexPlatform")


class DiscordChannel(Enum):
    """Discord channel types for routing notifications."""
    TRADES = "trades"
    RISK = "risk"
    HEALTH = "health"
    REPORTS = "reports"
    DEFAULT = "default"


class DiscordNotifier:
    """
    Multi-channel Discord notification service.
    
    Routes messages to appropriate channels based on event type.
    Falls back to main webhook if channel-specific webhooks are not configured.
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        # Main/fallback webhook
        self.main_webhook = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        
        # Channel-specific webhooks (fallback to main if not set)
        self.webhooks = {
            DiscordChannel.TRADES: os.getenv("DISCORD_WEBHOOK_TRADES") or self.main_webhook,
            DiscordChannel.RISK: os.getenv("DISCORD_WEBHOOK_RISK") or self.main_webhook,
            DiscordChannel.HEALTH: os.getenv("DISCORD_WEBHOOK_HEALTH") or self.main_webhook,
            DiscordChannel.REPORTS: os.getenv("DISCORD_WEBHOOK_REPORTS") or self.main_webhook,
            DiscordChannel.DEFAULT: self.main_webhook,
        }
        
        self.enabled = bool(self.main_webhook)
        if not self.enabled:
            logger.warning("DiscordNotifier disabled: No DISCORD_WEBHOOK_URL found.")

    def _get_webhook(self, channel: DiscordChannel) -> Optional[str]:
        """Get webhook URL for specified channel."""
        return self.webhooks.get(channel, self.main_webhook)

    def send_message(self, content: str, username: str = "Forex Agent", 
                     channel: DiscordChannel = DiscordChannel.DEFAULT):
        """Sends a simple text message to Discord."""
        if not self.enabled:
            return

        data = {
            "content": content,
            "username": username
        }
        self._post(data, channel)

    def send_trade_alert(self, signal: Dict[str, Any], order_intent: Any, result: Any):
        """Sends a rich formatted embed for a trade execution."""
        if not self.enabled:
            return

        status_emoji = "✅" if result.status in ["FILLED", "SUBMITTED"] else "❌"
        color = 5763719 if result.status in ["FILLED", "SUBMITTED"] else 15548997  # Green / Red

        # Format timestamp with timezone
        ts = signal.get('timestamp')
        if hasattr(ts, 'isoformat'):
            ts_str = ts.isoformat()
        else:
            ts_str = datetime.now(timezone.utc).isoformat()

        embed = {
            "title": f"{status_emoji} {'FILLED' if result.status in ['FILLED', 'SUBMITTED'] else 'REJECTED'}: {signal['direction']} {signal['symbol']}",
            "color": color,
            "fields": [
                {"name": "⏰ Time", "value": ts_str[:19].replace('T', ' '), "inline": True},
                {"name": "📊 Status", "value": result.status, "inline": True},
                {"name": "📐 Size", "value": f"{order_intent.quantity} lots", "inline": True},
                {"name": "💵 Entry", "value": f"{signal.get('entry_price', 'N/A')}", "inline": True},
                {"name": "🛑 SL", "value": f"{signal.get('stop_loss', 'N/A')}", "inline": True},
                {"name": "🎯 TP", "value": f"{signal.get('take_profit', 'N/A')}", "inline": True},
                {"name": "📝 Rationale", "value": signal.get('rationale', 'No rationale provided')[:500], "inline": False},
            ],
            "footer": {
                "text": f"🆔 {result.broker_order_id if result.broker_order_id else 'N/A'} | Source: IG"
            },
            "timestamp": ts_str if hasattr(ts, 'isoformat') else None
        }

        data = {
            "username": "Forex Execution",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.TRADES)

    def send_error(self, message: str):
        """Sends an error alert to the health channel."""
        if not self.enabled:
            return

        embed = {
            "title": "🚨 CRITICAL ERROR",
            "description": message,
            "color": 15548997,  # Red
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        data = {
            "username": "Forex Alert",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.HEALTH)

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
                {"name": "📈 Entry", "value": f"{trade.get('entry_price', 'N/A')}", "inline": True},
                {"name": "📉 Exit", "value": f"{trade.get('exit_price', 'N/A')}", "inline": True},
                {"name": "💵 PnL", "value": pnl_str, "inline": True},
                {"name": "📐 Size", "value": f"{trade.get('quantity', 'N/A')}", "inline": True},
            ],
            "footer": {"text": f"🆔 {trade.get('broker_order_id', 'N/A')}"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        data = {
            "username": "Forex Execution",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.TRADES)

    def send_risk_alert(self, alert_type: str, details: Dict[str, Any]):
        """
        Sends a risk alert to the risk channel.
        
        Args:
            alert_type: Type of risk event (e.g., "DAILY_LOSS_LIMIT", "MAX_EXPOSURE")
            details: Dict with keys like 'current', 'limit', 'action'
        """
        if not self.enabled:
            return

        embed = {
            "title": "🚨 RISK LIMIT HIT",
            "color": 16744256,  # Orange
            "fields": [
                {"name": "⚠️ Type", "value": alert_type, "inline": False},
                {"name": "📊 Current", "value": str(details.get('current', 'N/A')), "inline": True},
                {"name": "🛑 Limit", "value": str(details.get('limit', 'N/A')), "inline": True},
                {"name": "🔧 Action", "value": details.get('action', 'Trading PAUSED'), "inline": False},
            ],
            "footer": {"text": f"⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        data = {
            "username": "Risk Monitor",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.RISK)

    def send_health_status(self, status: str, details: Dict[str, Any]):
        """
        Sends a health status update to the health channel.
        
        Args:
            status: Overall status (e.g., "OK", "DEGRADED", "DOWN")
            details: Dict with keys like 'broker', 'data_feed', 'db', 'uptime'
        """
        if not self.enabled:
            return

        # Color based on status
        color_map = {"OK": 5763719, "DEGRADED": 16744256, "DOWN": 15548997}
        status_emoji = {"OK": "🟢", "DEGRADED": "🟡", "DOWN": "🔴"}.get(status, "⚪")

        embed = {
            "title": f"{status_emoji} SYSTEM HEALTH — {status}",
            "color": color_map.get(status, 9807270),
            "fields": [
                {"name": "🔗 Broker", "value": details.get('broker', 'Unknown'), "inline": True},
                {"name": "📡 Data Feed", "value": details.get('data_feed', 'Unknown'), "inline": True},
                {"name": "🕐 Last Candle", "value": details.get('last_candle', 'N/A'), "inline": True},
                {"name": "💾 DB", "value": details.get('db', 'Unknown'), "inline": True},
                {"name": "⚙️ Uptime", "value": details.get('uptime', 'N/A'), "inline": True},
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        data = {
            "username": "Health Monitor",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.HEALTH)

    def send_daily_summary(self, summary: Dict[str, Any]):
        """Sends an end-of-day summary report to the reports channel."""
        if not self.enabled:
            return

        total_pnl = summary.get("total_pnl", 0)
        is_profit = total_pnl >= 0
        color = 5763719 if is_profit else 15548997
        pnl_emoji = "📈" if is_profit else "📉"
        pnl_str = f"+{total_pnl:.2f}" if is_profit else f"{total_pnl:.2f}"

        # Build fields
        fields = [
            {"name": "📊 Trades", "value": str(summary.get("total_trades", 0)), "inline": True},
            {"name": "✅ Wins", "value": str(summary.get("wins", 0)), "inline": True},
            {"name": "❌ Losses", "value": str(summary.get("losses", 0)), "inline": True},
            {"name": f"{pnl_emoji} PnL", "value": pnl_str, "inline": True},
            {"name": "💰 Equity", "value": f"{summary.get('equity', 'N/A')}", "inline": True},
            {"name": "🎯 Win Rate", "value": f"{summary.get('win_rate', 0):.1f}%", "inline": True},
        ]

        # Add optional fields
        if summary.get("biggest_win"):
            fields.append({"name": "🏆 Biggest Win", "value": f"+{summary['biggest_win']:.2f}", "inline": True})
        if summary.get("biggest_loss"):
            fields.append({"name": "💔 Biggest Loss", "value": f"{summary['biggest_loss']:.2f}", "inline": True})
        if summary.get("errors_count") is not None:
            fields.append({"name": "🛑 Errors", "value": str(summary['errors_count']), "inline": True})

        embed = {
            "title": f"📊 DAILY REPORT — {summary.get('date', 'Today')}",
            "color": color,
            "fields": fields,
            "footer": {"text": "End of Day Report"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        data = {
            "username": "Forex Daily",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.REPORTS)

    def send_weekly_summary(self, summary: Dict[str, Any]):
        """Sends a weekly summary report to the reports channel."""
        if not self.enabled:
            return

        total_pnl = summary.get("total_pnl", 0)
        is_profit = total_pnl >= 0
        color = 5763719 if is_profit else 15548997
        pnl_emoji = "📈" if is_profit else "📉"
        pnl_str = f"+{total_pnl:.2f}" if is_profit else f"{total_pnl:.2f}"

        embed = {
            "title": f"📅 WEEKLY REPORT — {summary.get('week', 'This Week')}",
            "color": color,
            "fields": [
                {"name": "📊 Total Trades", "value": str(summary.get("total_trades", 0)), "inline": True},
                {"name": f"{pnl_emoji} PnL", "value": pnl_str, "inline": True},
                {"name": "🎯 Win Rate", "value": f"{summary.get('win_rate', 0):.1f}%", "inline": True},
                {"name": "📉 Max Drawdown", "value": f"{summary.get('max_drawdown', 0):.2f}%", "inline": True},
                {"name": "🛑 Risk Events", "value": str(summary.get("risk_events", 0)), "inline": True},
                {"name": "⚠️ Errors", "value": str(summary.get("errors_count", 0)), "inline": True},
            ],
            "footer": {"text": "Weekly Performance Report"},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        data = {
            "username": "Forex Weekly",
            "embeds": [embed]
        }
        self._post(data, DiscordChannel.REPORTS)

    def _post(self, data: Dict[str, Any], channel: DiscordChannel = DiscordChannel.DEFAULT):
        """Post data to the appropriate Discord webhook."""
        webhook_url = self._get_webhook(channel)
        if not webhook_url:
            logger.warning(f"No webhook URL for channel {channel.value}")
            return

        try:
            response = requests.post(webhook_url, json=data, timeout=10)
            response.raise_for_status()
            logger.debug(f"Discord notification sent to {channel.value}")
        except requests.Timeout:
            logger.warning(f"Discord notification timed out (10s) for {channel.value}")
        except requests.RequestException as e:
            logger.error(f"Discord notification failed for {channel.value}: {e}")
