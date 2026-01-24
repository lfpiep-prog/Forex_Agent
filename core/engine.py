
import logging
import time
from execution.brokers.mock_broker import MockBroker
from execution.brokers.ig_broker import IGBroker
from execution.strategies.baseline_sma_cross import BaselineSMACross
from execution.risk_eval import evaluate_risk
from execution.risk_limits import RiskConfig
from execution.execute_order import ExecutionRouter, OrderIntent
from execution.verify_full_pipeline import generate_dummy_data # Reuse for now
from data.mcp_client import MCPDataClient
from data.yfinance_provider import YFinanceDataProvider
import uuid

logger = logging.getLogger("ForexPlatform")

class TradingEngine:
    def __init__(self, mode="MOCK", strategy_name="SMA_CROSS"):
        self.mode = mode
        self.strategy_name = strategy_name
        self.running = False
        
        # Initialize Broker
        if self.mode == "LIVE":
            self.broker = IGBroker()
        else:
            # MOCK and PAPER modes use MockBroker for execution
            self.broker = MockBroker()
            
        # Initialize Data Providers
        self.mcp_client = MCPDataClient()
        self.market_data = YFinanceDataProvider()
            
        # Initialize Strategy (Plugin loader would go here)
        if self.strategy_name == "SMA_CROSS":
            self.strategy = BaselineSMACross(fast_period=50, slow_period=200)
        else:
            raise NotImplementedError(f"Strategy {strategy_name} not found")
            
        # Initialize Components
        self.router = ExecutionRouter(self.broker)
        # Load Risk Config form file later
        self.risk_config = RiskConfig(
            max_daily_loss_pct=2.0, max_trades_per_day=5,
            risk_per_trade_pct=1.0, max_open_lots=5.0
        )
        
    def run_cycle(self):
        """Runs a single logic cycle: Data -> Signal -> Risk -> Execution"""
        logger.info(f"--- Starting Cycle [{self.mode}] ---")
        
        # 1. Data
        if self.mode in ["LIVE", "PAPER"]:
             logger.info("Fetching Live Data via YFinance...")
             # Fetch enough data for the strategy (200 SMA needs 200+ candles)
             df = self.market_data.fetch_latest_candles("EUR_USD", period="5d", interval="5m")
             
             if df.empty:
                 logger.error("Failed to fetch live data. Aborting cycle.")
                 return
        else:
             # MOCK mode uses purely synthetic data
             df = generate_dummy_data()
        
        # Detect symbol from data
        symbol = df.iloc[0]['symbol'] if not df.empty else "EUR_USD"

        # 1.5 Fetch Context Data (MCP)
        logger.info(f"Fetching Sentiment for {symbol}...")
        sentiment = self.mcp_client.get_sentiment(symbol)
        context = {"sentiment": sentiment}
             
        # 2. Signal
        logger.info(f"Running Strategy with Context: {context}")
        signals = self.strategy.calculate(df, context=context)
        
        if not signals:
            logger.info("No signals (Filtered or None).")
            return

        latest_signal = signals[-1]
        logger.info(f"Signal Found: {latest_signal}")
        
        # 3. Risk
        balance_info = self.broker.get_balance()
        if not balance_info:
            balance_info = {"balance": 10000, "equity": 10000, "daily_loss": 0}
            
        risk_intent = evaluate_risk(latest_signal, balance_info, self.risk_config)
        
        if not risk_intent.valid:
            logger.info(f"Risk Rejected: {risk_intent.reason}")
            return

        # 4. Execution
        order_intent = OrderIntent(
            idempotency_key=str(uuid.uuid4()),
            symbol=risk_intent.symbol,
            direction=risk_intent.direction,
            quantity=int(risk_intent.size * 100000), # Units
            order_type="MARKET"
        )
        
        result = self.router.execute_order(order_intent)
        logger.info(f"Execution Result: {result}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # Use PAPER mode to test Real Data + Mock Execution
    engine = TradingEngine(mode="PAPER")
    engine.run_cycle()
