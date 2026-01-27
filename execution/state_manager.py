import json
import os
import logging
from datetime import datetime

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "state.json")
logger = logging.getLogger("StateManager")

class StateManager:
    def __init__(self, file_path=STATE_FILE):
        self.file_path = file_path
        self._ensure_dir()

    def _ensure_dir(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def load_state(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_state(self, state):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def is_candle_processed(self, symbol: str, timeframe: str, timestamp: str) -> bool:
        """
        Checks if the candle (identified by timestamp) has already been processed.
        """
        state = self.load_state()
        key = f"{symbol}_{timeframe}"
        last_processed = state.get(key)
        
        if last_processed == timestamp:
            return True
        return False

    def mark_candle_processed(self, symbol: str, timeframe: str, timestamp: str):
        """
        Updates the state to mark this candle as processed.
        """
        state = self.load_state()
        key = f"{symbol}_{timeframe}"
        state[key] = timestamp
        self.save_state(state)
