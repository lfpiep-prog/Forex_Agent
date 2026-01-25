
import os
import sys
import pandas as pd
import time
from datetime import datetime, timezone, timedelta
import uuid

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from execution import market_data as data, risk
from execution.logger import setup_logger, PipelineLogger
from execution.generate_signals import SignalGenerator
from execution.config import config
from execution.execute_order import ExecutionRouter, OrderIntent
from execution.brokers.mock_broker import MockBroker
from execution.brokers.ig_broker import IGBroker
from execution.account import AccountManager
from execution.filters import TimeFilter
from data.mcp_client import MCPDataClient
from execution.state_manager import StateManager
from execution.notifier import DiscordNotifier

def check_time_constraints(log, plog):
    """Checks if trading is allowed at the current time."""
    time_filter = TimeFilter()
    is_open, time_reason = time_filter.is_trading_allowed(datetime.utcnow())
    
    if not is_open:
        log.info(f"Step 1 [Time]: BLOCKED ({time_reason})")
        plog.update(reason=f"Time: {time_reason}")
        return False
        
    log.info("Step 1 [Time]: PASSED")
    return True

def fetch_and_prepare_data(log, plog):
    """Fetches and normalizes price data with retry logic for delayed candles."""
    
    # Target: The candle that just closed (Current Hour rounded down - 1h)
    now = datetime.now(timezone.utc)
    current_hour_socket = now.replace(minute=0, second=0, microsecond=0)
    target_candle_time = current_hour_socket - timedelta(hours=1)
    
    log.info(f"Step 2 [Data]: Fetching {config.SYMBOL} ({config.TIMEFRAME})... Expecting Candle: {target_candle_time.isoformat()}")

    df = None
    
    for attempt in range(config.DATA_RETRY_ATTEMPTS):
        raw_prices = data.fetch_prices(config.SYMBOL, config.TIMEFRAME)
        
        if raw_prices:
            df = data.normalize(raw_prices)
            
            # Check if we have the latest candle
            if not df.empty:
                last_candle_ts = pd.to_datetime(df.iloc[-1]['timestamp'], utc=True) if df.iloc[-1]['timestamp'] else None
                # Handle timezone naive vs aware
                if last_candle_ts and last_candle_ts.tzinfo is None:
                     last_candle_ts = last_candle_ts.replace(tzinfo=timezone.utc)
                
                if last_candle_ts == target_candle_time:
                    log.info(f"Step 2 [Data]: Success. Found candle {last_candle_ts}.")
                    break
                else:
                    log.warning(f"Step 2 [Data]: Stale Data (Last: {last_candle_ts}, Expected: {target_candle_time}). Retrying ({attempt+1}/{config.DATA_RETRY_ATTEMPTS})...")
            else:
                log.warning(f"Step 2 [Data]: Empty Dataframe. Retrying...")
        else:
             log.warning(f"Step 2 [Data]: Fetch Failed. Retrying...")
             
        if attempt < config.DATA_RETRY_ATTEMPTS - 1:
            time.sleep(config.DATA_RETRY_DELAY)
            
    if df is None or df.empty:
        log.warning("Step 2 [Data]: FAILED (No Data after retries)")
        plog.update(reason="Data: No prices returned")
        return None

    # Final check (soft fail: proceed with what we have, but log warning, OR hard fail?)
    # Decision: Proceed, but we rely on Timestamp for idempotency. 
    # If we process an OLD candle, idempotency check (Step 3 pre-check) should catch it if it was already processed.
    # If it wasn't processed (e.g. system down), we process it now. ACCEPTABLE.
    
    current_price = df.iloc[-1]['close'] if not df.empty else 0
    plog.update(price=current_price)
    
    # Return both DF and the timestamp of the last candle for idempotency
    return df

def analyze_market(log, df, plog):
    """Generates trading signals from the data."""
    log.info("Step 3 [Strategy]: Analyzing...")
    
    if df.empty: return None

    # Idempotency Check
    state_manager = StateManager()
    last_candle_ts = df.iloc[-1]['timestamp']
    # Ensure string format for JSON
    ts_str = last_candle_ts.isoformat() if hasattr(last_candle_ts, 'isoformat') else str(last_candle_ts)
    
    if state_manager.is_candle_processed(config.SYMBOL, config.TIMEFRAME, ts_str):
        log.info(f"Step 3 [Strategy]: SKIPPED. Candle {ts_str} already processed.")
        plog.update(decision="SKIPPED", reason="Idempotency: Candle already processed")
        return None

    engine = SignalGenerator(config.STRATEGY, config.STRATEGY_PARAMS)
    signals = engine.generate(df)
    
    latest_signal = signals[-1] if signals else None
    
    if not latest_signal or latest_signal['direction'] not in ['LONG', 'SHORT']:
        log.info("Step 3 [Strategy]: NO SIGNAL")
        plog.update(signal="HOLD", reason="Strategy: No Signal")
        # Mark as processed because we analyzed it and found nothing
        state_manager.mark_candle_processed(config.SYMBOL, config.TIMEFRAME, ts_str)
        return None

    plog.update(signal=latest_signal['direction'])
    log.info(f"Step 3 [Strategy]: SIGN: {latest_signal['direction']}")
    return latest_signal

def check_news_sentiment(log, latest_signal, plog):
    """Filters signals based on news sentiment."""
    log.info("Step 4 [News]: Checking Sentiment...")
    mcp = MCPDataClient()
    sentiment = mcp.get_sentiment(config.SYMBOL)
    plog.update(sentiment=sentiment)
    
    is_news_valid = True
    news_reason = "Confirmed"
    
    if latest_signal['direction'] == 'LONG' and sentiment == 'BEARISH':
        is_news_valid = False
        news_reason = "Sentiment Bearish vs Long"
    elif latest_signal['direction'] == 'SHORT' and sentiment == 'BULLISH':
        is_news_valid = False
        news_reason = "Sentiment Bullish vs Short"
        
    if not is_news_valid:
        log.info(f"Step 4 [News]: BLOCKED ({news_reason})")
        plog.update(decision="BLOCKED_NEWS", reason=news_reason)
        return False
        
    log.info(f"Step 4 [News]: PASSED ({sentiment})")
    return True

def assess_risk(log, latest_signal, plog):
    """Calculates position size and validates risk."""
    log.info("Step 5 [Risk]: Calculating Size...")
    
    # Sync Live Equity First
    account_mgr = AccountManager()
    if config.BROKER == 'ig':
        try:
            broker_sync = IGBroker()
            if broker_sync.connect():
                bal = broker_sync.get_balance()
                if bal and bal.get('equity'):
                    account_mgr.reset(bal.get('equity'))
                    log.info(f"Live Equity: {bal.get('equity')}")
        except Exception as e:
            log.warning(f"Live Sync Failed: {e}")

    # Evaluate Risk
    is_safe, risk_reason, recommended_lots = risk.risk_eval(latest_signal, account_mgr.get_snapshot())
    
    if not is_safe:
        log.info(f"Step 5 [Risk]: BLOCKED ({risk_reason})")
        plog.update(decision="BLOCKED_RISK", reason=risk_reason)
        return False

    # Extract Size from Risk Calc
    lots = recommended_lots
    plog.update(size=lots)
    log.info(f"Step 5 [Risk]: PASSED (Size: {lots})")
    return lots

def execute_trade(log, latest_signal, lots, plog):
    """Executes the trade order."""
    log.info("Step 6 [Exec]: Submitting Order...")
    
    exec_intent = OrderIntent(
        idempotency_key=str(uuid.uuid4()),
        symbol=config.SYMBOL,
        direction=latest_signal['direction'],
        quantity=float(lots),
        order_type="MARKET",
        limit_price=None,
        sl_distance=None, 
        tp_distance=None
    )
    
    # Calculate SL/TP Distances for IG logic if needed (Points)
    is_jpy = "JPY" in config.SYMBOL
    point_size = 0.01 if is_jpy else 0.0001
    if latest_signal.get('stop_loss') and latest_signal.get('entry_price'):
        exec_intent.sl_distance = abs(latest_signal['entry_price'] - latest_signal['stop_loss']) / point_size
    if latest_signal.get('take_profit') and latest_signal.get('entry_price'):
        exec_intent.tp_distance = abs(latest_signal['take_profit'] - latest_signal['entry_price']) / point_size

    if config.BROKER == 'ig':
        broker = IGBroker()
    else:
        broker = MockBroker()
        
    router = ExecutionRouter(broker)
    result = router.execute_order(exec_intent)
    
    log.info(f"Step 6 [Exec]: DONE (Status: {result.status})")
    
    plog.update(decision=result.status, reason="Executed" if result.status in ["FILLED", "SUBMITTED"] else f"Exec Failed: {result.error_message}")

    # --- NOTIFICATION ---
    if result.status in ["FILLED", "SUBMITTED"]:
        notifier = DiscordNotifier()
        notifier.send_trade_alert(latest_signal, exec_intent, result)
    
    # Mark processed after attempt (whether successful or not, we intend to not retry this candle blindly)
    # Ideally only on success, but to prevent loops on failure, we mark it.
    # User can delete state.json entry if they want to force retry.
    state_manager = StateManager()
    # Need to get the candle timestamp again... strictly speaking we should pass it down.
    # Instead, we rely on the fact that analyze_market would have returned None if processed.
    # Wait, analyze_market ONLY marks processed if NO SIGNAL. 
    # If there IS a signal, it returns it. We execute. THEN we must mark processed.
    # We need the timestamp here.
    pass # Managed in run_pipeline now

def run_pipeline():
    log = setup_logger()
    
    with PipelineLogger() as plog:
        try:
            plog.update(symbol=config.SYMBOL)
            log.info("--- PIPELINE START ---")
            
            if not check_time_constraints(log, plog): return
            
            df = fetch_and_prepare_data(log, plog)
            if df is None: return

            latest_signal = analyze_market(log, df, plog)
            if latest_signal is None: return

            if not check_news_sentiment(log, latest_signal, plog): return

            lots = assess_risk(log, latest_signal, plog)
            if lots is False: return

            execute_trade(log, latest_signal, lots, plog)
            
            # Mark processed for the Signal Case
            state_manager = StateManager()
            last_candle_ts = df.iloc[-1]['timestamp']
            ts_str = last_candle_ts.isoformat() if hasattr(last_candle_ts, 'isoformat') else str(last_candle_ts)
            state_manager.mark_candle_processed(config.SYMBOL, config.TIMEFRAME, ts_str)

        except Exception as e:
            msg = f"Critical Pipeline Error: {e}"
            log.error(msg, exc_info=True)
            # Send Critical Alert
            DiscordNotifier().send_error(msg)
            # PipelineLogger.__exit__ will handle exception logging
            raise e 

if __name__ == "__main__":
    run_pipeline()
