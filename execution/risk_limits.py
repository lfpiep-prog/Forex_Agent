"""
Risk Limits Module

Checks account risk limits and sends Discord alerts when limits are hit.
"""

from dataclasses import dataclass
from typing import Dict, Optional
import logging

logger = logging.getLogger("ForexPlatform")


@dataclass
class RiskConfig:
    """Configuration for risk management parameters."""
    max_daily_loss_pct: float = 2.0
    max_trades_per_day: int = 5
    risk_per_trade_pct: float = 1.0
    max_open_lots: float = 1.0
    sl_pips_default: float = 20.0
    tp_pips_default: float = 40.0
    min_sl_pips: float = 5.0
    use_trailing_stop: bool = False


class RiskManager:
    """
    Manages risk limits and sends Discord alerts when limits are breached.
    """
    
    def __init__(self, config: Optional[RiskConfig] = None, notifier=None):
        self.config = config or RiskConfig()
        self._notifier = notifier
        
    @property
    def notifier(self):
        """Lazy load notifier to avoid circular imports."""
        if self._notifier is None:
            from execution.notifier import DiscordNotifier
            self._notifier = DiscordNotifier()
        return self._notifier

    def check_daily_limits(self, account_snapshot: Dict) -> Dict:
        """
        Checks if account is within daily risk limits.
        Sends Discord alert if limit is hit.
        
        Returns: {"allowed": bool, "reason": str, "alert_sent": bool}
        """
        result = {"allowed": True, "reason": "OK", "alert_sent": False}
        
        # 1. Daily Loss Limit
        current_loss = account_snapshot.get("daily_loss_current", 0.0)
        equity = account_snapshot.get("equity", 1000.0)
        
        if equity <= 0:
            result = {
                "allowed": False, 
                "reason": "EQUITY_ZERO_OR_NEGATIVE",
                "alert_sent": self._send_alert(
                    "EQUITY_ZERO_OR_NEGATIVE",
                    {"current": f"${equity:.2f}", "limit": "> $0", "action": "Trading HALTED - Critical error"}
                )
            }
            return result

        loss_pct = (current_loss / equity) * 100.0
        
        if loss_pct >= self.config.max_daily_loss_pct:
            result = {
                "allowed": False, 
                "reason": f"DAILY_LOSS_LIMIT_REACHED: {loss_pct:.2f}% >= {self.config.max_daily_loss_pct}%",
                "alert_sent": self._send_alert(
                    "DAILY_LOSS_LIMIT",
                    {
                        "current": f"{loss_pct:.2f}%",
                        "limit": f"{self.config.max_daily_loss_pct}%",
                        "action": "Trading PAUSED until next day"
                    }
                )
            }
            return result

        # 2. Daily Trades Count
        daily_trades = account_snapshot.get("daily_trades_count", 0)
        if daily_trades >= self.config.max_trades_per_day:
            result = {
                "allowed": False,
                "reason": f"MAX_TRADES_LIMIT_REACHED: {daily_trades} >= {self.config.max_trades_per_day}",
                "alert_sent": self._send_alert(
                    "MAX_TRADES_LIMIT",
                    {
                        "current": str(daily_trades),
                        "limit": str(self.config.max_trades_per_day),
                        "action": "No more trades today"
                    }
                )
            }
            return result

        return result

    def check_exposure_limits(self, account_snapshot: Dict, new_size_lots: float) -> Dict:
        """
        Checks if adding new trade size would breach max exposure limits.
        Sends Discord alert if limit would be breached.
        
        Returns: {"allowed": bool, "reason": str, "alert_sent": bool}
        """
        current_open_lots = 0.0
        for trade in account_snapshot.get("open_positions", []):
            current_open_lots += trade.get("size", 0.0)
            
        projected_lots = current_open_lots + new_size_lots
        
        if projected_lots > self.config.max_open_lots:
            return {
                "allowed": False, 
                "reason": f"MAX_EXPOSURE_LIMIT: {projected_lots:.2f} > {self.config.max_open_lots}",
                "alert_sent": self._send_alert(
                    "MAX_EXPOSURE_LIMIT",
                    {
                        "current": f"{current_open_lots:.2f} lots",
                        "limit": f"{self.config.max_open_lots} lots",
                        "action": f"Rejected new order of {new_size_lots:.2f} lots"
                    }
                )
            }
            
        return {"allowed": True, "reason": "OK", "alert_sent": False}

    def _send_alert(self, alert_type: str, details: Dict) -> bool:
        """Send risk alert via Discord. Returns True if sent successfully."""
        try:
            self.notifier.send_risk_alert(alert_type, details)
            logger.info(f"Risk alert sent: {alert_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to send risk alert: {e}")
            return False


# Legacy function wrappers for backward compatibility
def check_daily_limits(account_snapshot: Dict, config: RiskConfig) -> Dict:
    """
    Legacy function - checks if account is within daily risk limits.
    Returns: {"allowed": bool, "reason": str}
    """
    manager = RiskManager(config)
    result = manager.check_daily_limits(account_snapshot)
    return {"allowed": result["allowed"], "reason": result["reason"]}


def check_exposure_limits(account_snapshot: Dict, new_size_lots: float, config: RiskConfig) -> Dict:
    """
    Legacy function - checks if adding new trade size would breach max exposure limits.
    """
    manager = RiskManager(config)
    result = manager.check_exposure_limits(account_snapshot, new_size_lots)
    return {"allowed": result["allowed"], "reason": result["reason"]}
