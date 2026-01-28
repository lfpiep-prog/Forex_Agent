
import os
from dotenv import load_dotenv
load_dotenv()
from execution.risk_limits import RiskConfig

class Config:
    # Trading Parameters
    SYMBOL = "USDJPY"
    TIMEFRAME = "H1"
    
    # Strategy
    STRATEGY = "baseline_sma_cross"
    # Winner: SMA 10/30 (Aggressive)
    STRATEGY_PARAMS = {"fast_period": 10, "slow_period": 30, "use_rsi_filter": True}
    
    # Risk Management
    RISK_CONFIG = RiskConfig(
        max_daily_loss_pct=5.0, # Increased for compounding breathing room
        max_trades_per_day=10,
        risk_per_trade_pct=2.0, # Aligned with Compounding logic

        max_open_lots=5.0,
        sl_pips_default=30.0,
        tp_pips_default=60.0
    )
    
    # System
    LOG_LEVEL = "INFO"
    DATA_PROVIDER = os.getenv("DATA_PROVIDER", "polygon") # Options: yfinance, mock, ig, twelvedata, polygon
    BROKER = os.getenv("BROKER", "ig") # Options: mock, ig

    # Safety & Broker
    LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
    BROKER_ALLOWLIST = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD"] # Allowed execution symbols

    # Resilience
    DATA_RETRY_ATTEMPTS = 3
    DATA_RETRY_DELAY = 10 # seconds

# Instance for easy import
config = Config()
