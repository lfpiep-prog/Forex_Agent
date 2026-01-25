import json
from abc import ABC, abstractmethod
from typing import Optional, Dict
from trading_ig import IGService
from execution.models import OrderIntent, OrderResult
from core.config import settings
from core.logger import get_logger
from core.interfaces import IBroker

logger = get_logger("IGBroker")
from execution.safety import SafetyGate

class IGBroker(IBroker):
    """
    IG Markets Broker Implementation.
    """
    def __init__(self):
        self.username = settings.IG_USERNAME
        self.password = settings.IG_PASSWORD
        self.api_key = settings.IG_API_KEY
        self.acc_type = settings.IG_ACC_TYPE
        
        self.ig_service = IGService(
            self.username, self.password, self.api_key, self.acc_type
        )
        self.connected = False
        self._instruments_cache: Dict[str, dict] = {}
        self._processed_keys = set()

    def connect(self) -> bool:
        if self.connected: 
            return True
            
        try:
            logger.info("Connecting to IG Markets...")
            self.ig_service.create_session()
            self.connected = True
            logger.info("IG Connected Successfully.")
            return True
        except Exception as e:
            logger.error(f"IG Connection Failed: {e}")
            return False

    def get_balance(self) -> Optional[Dict[str, float]]:
        """Returns {balance, equity, available}"""
        if not self.connect(): return None
        
        try:
            # Fetch accounts
            accounts = self.ig_service.fetch_accounts()
            
            # If dataframe
            if hasattr(accounts, 'iloc'):
                row = accounts.iloc[0]
                return {
                    "balance": float(row.get('balance', 0)),
                    "equity": float(row.get('balance', 0)) + float(row.get('profitLoss', 0)), 
                    "available": float(row.get('available', 0))
                }
            else:
                logger.warning(f"Unexpected account data format: {type(accounts)}")
                return {"balance": 0.0, "equity": 0.0}

        except Exception as e:
            logger.error(f"Failed to fetch balance: {e}")
            return None

    def _get_instrument(self, symbol: str) -> Optional[dict]:
        """Lazy loads instrument config from JSON."""
        if not self._instruments_cache:
            try:
                config_path = "config/instruments.json" # Simplified path for container context or relative to cwd
                # Better: usage `pathlib` or robust path finding.
                # Re-adding import os is safer for now if I removed it.
                with open(config_path, 'r') as f:
                    self._instruments_cache = json.load(f)
            except Exception as e:
                logger.error(f"Could not load instruments.json: {e}")
                return None
        
        return self._instruments_cache.get(symbol)

    def execute_order(self, order_intent: OrderIntent) -> OrderResult:
        """
        Executes a market order using IG API with Safety Gates and Idempotency.
        """
        # --- SAFETY GATES ---
        # 1. Intent Validation (Allowlist, Size Sanity)
        if not SafetyGate.validate_intent(order_intent):
            return OrderResult(status="FAILED", error_message="Safety Gate: Invalid Intent or Symbol not allowed")

        # 2. Live Execution Guard
        if self.acc_type == "LIVE":
            if not SafetyGate.is_live_allowed(self.acc_type):
                msg = "Safety Gate: Live Trading BLOCKED. Set LIVE_TRADING_ENABLED=true to confirm."
                logger.critical(msg)
                return OrderResult(status="FAILED", error_message=msg)

        # 3. Idempotency Check
        idem_key = SafetyGate.generate_idempotency_key(order_intent)
        if idem_key in self._processed_keys:
            msg = f"Idempotency Check: Order {idem_key} already processed. Skipping."
            logger.warning(msg)
            # Return SKIPPED or cached result if we had it. For now, FAILED/SKIPPED to avoid double fill.
            return OrderResult(status="SKIPPED", error_message="Duplicate Order")

        # --- EXECUTION ---
        if not self.connect():
            return OrderResult(status="FAILED", error_message="Not connected")
            
        symbol = order_intent.symbol
        instrument_config = self._get_instrument(symbol)
        
        if not instrument_config:
             return OrderResult(status="FAILED", error_message=f"Instrument config not found for {symbol}")

        epic = instrument_config.get("epic")
        currency_code = instrument_config.get("currency", "USD")
        min_size = instrument_config.get("min_size", 0.1)
        
        # Prepare Size
        contracts = round(abs(order_intent.quantity), 2)
        if contracts < min_size: 
            logger.warning(f"Calculated size {contracts} < min {min_size}. Clamping to min.")
            contracts = min_size

        try:
            # Prepare Direction
            direction = order_intent.direction.upper()
            ig_direction = "BUY" if direction in ["LONG", "BUY"] else "SELL"
            
            # Prepare SL/TP logic
            sl_dist = round(float(order_intent.sl_distance), 1) if order_intent.sl_distance else None
            tp_dist = round(float(order_intent.tp_distance), 1) if order_intent.tp_distance else None
            
            # Log Intent (Safe)
            logger.info(f"INTENT: {ig_direction} {contracts} {symbol} (SL:{sl_dist}, TP:{tp_dist}). Executing...")

            response = self.ig_service.create_open_position(
                currency_code=currency_code,
                direction=ig_direction,
                epic=epic,
                expiry='-',
                force_open='true',
                guaranteed_stop='false',
                level=None,
                limit_level=None,
                limit_distance=tp_dist, 
                order_type='MARKET',
                quote_id=None,
                size=contracts, 
                stop_level=None,
                stop_distance=sl_dist, 
                trailing_stop=False,
                trailing_stop_increment=None
            )
            
            if not response:
                raise Exception("Empty response from IG API")

            deal_ref = response.get('dealReference')
            logger.info(f"Order Submitted. Deal Ref: {deal_ref}")
            
            # Mark as processed only on successful submission
            self._processed_keys.add(idem_key)
            
            return OrderResult(
                status="SUBMITTED",
                broker_order_id=deal_ref,
                filled_quantity=contracts,
                filled_price=None # Unknown until confirmed
            )
            
        except Exception as e:
            logger.error(f"IG Order Error: {e}", exc_info=True)
            return OrderResult(
                status="FAILED",
                error_message=str(e)
            )
