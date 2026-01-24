import json
import os

class AccountManager:
    def __init__(self, initial_balance=10000.0, storage_file="balance.json"):
        self.storage_file = storage_file
        self.balance = initial_balance
        self.equity = initial_balance
        # In a real app, we'd load existing balance. 
        # For this session, we might want to reset or load. 
        # Let's verify file existence.
        self._load()

    def _load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    self.balance = data.get('balance', self.balance)
                    self.equity = data.get('equity', self.equity)
            except:
                pass

    def _save(self):
        try:
            with open(self.storage_file, 'w') as f:
                json.dump({"balance": self.balance, "equity": self.equity}, f)
        except Exception:
            pass

    def update_balance(self, profit_loss):
        """Updates balance after a closed trade."""
        self.balance += profit_loss
        self.equity = self.balance # For MVP, assuming flattened usage
        self._save()

    def get_snapshot(self):
        return {
            "balance": self.balance,
            "equity": self.equity,
            "open_positions": [], 
            "daily_loss": 0.0 
        }

    def reset(self, amount=10000.0):
        self.balance = amount
        self.equity = amount
        self._save()
