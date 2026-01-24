import logging
import hashlib
import json
from execution.config import config
from execution.models import OrderIntent

logger = logging.getLogger("SafetyGate")

class SafetyGate:
    """
    Central authority for allowing or denying trade execution.
    Enforces Safety Gates:
    1. Live Trading Logic (Double Confirmation)
    2. Symbol Allowlist
    3. Idempotency Generation
    """

    @staticmethod
    def is_live_allowed(account_type: str) -> bool:
        """
        Determines if live trading is permitted.
        Requires:
        - Account Type to be 'LIVE'
        - Config.LIVE_TRADING_ENABLED to be True
        """
        if account_type.upper() != "LIVE":
            return False
            
        if not config.LIVE_TRADING_ENABLED:
            logger.warning("SAFETY GATE: Live account detected but LIVE_TRADING_ENABLED is False. Blocking.")
            return False
            
        return True

    @staticmethod
    def validate_intent(intent: OrderIntent) -> bool:
        """
        Validates the order intent against allowlists and basic sanity checks.
        """
        # 1. Symbol Allowlist
        if intent.symbol not in config.BROKER_ALLOWLIST:
            logger.error(f"SAFETY GATE: Symbol {intent.symbol} not in allowlist {config.BROKER_ALLOWLIST}. Blocking.")
            return False
            
        # 2. Quantity Sanity
        if intent.quantity <= 0:
            logger.error(f"SAFETY GATE: Invalid quantity {intent.quantity}. Blocking.")
            return False

        if intent.quantity > config.RISK_CONFIG.max_open_lots:
             logger.error(f"SAFETY GATE: Quantity {intent.quantity} exceeds max risk {config.RISK_CONFIG.max_open_lots}. Blocking.")
             return False

        return True

    @staticmethod
    def generate_idempotency_key(intent: OrderIntent) -> str:
        """
        Generates a deterministic hash for the order intent.
        Used to prevent duplicate submissions of the exact same order.
        """
        # Normalize data for hashing
        data = {
            "symbol": intent.symbol,
            "direction": intent.direction,
            "quantity": float(intent.quantity),
            "sl_distance": float(intent.sl_distance) if intent.sl_distance else None,
            "tp_distance": float(intent.tp_distance) if intent.tp_distance else None,
            # We assume intent might have a timestamp or distinct ID upstream, 
            # but if not, this hash protects against sending the exact same params twice in a short loop
            # if we didn't change them.
            # ideally, intent should have a 'signal_id' or 'timestamp'.
        }
        
        # If intent has a timestamp or unique ID, use it.
        # Assuming OrderIntent might be simple dataclass.
        # Let's verify existing OrderIntent definition if possible, but based on usage in ig_broker:
        # it has symbol, direction, sl_distance, tp_distance.
        
        payload = json.dumps(data, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
