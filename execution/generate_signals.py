import importlib
import sys
import os

# Ensure we can find the strategies
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SignalGenerator:
    """
    Engine to generate signals using a selected strategy.
    """
    def __init__(self, strategy_name, strategy_config=None):
        self.strategy_name = strategy_name
        self.strategy_config = strategy_config if strategy_config else {}
        self.strategy = self._load_strategy()

    # Registry of available strategies
    REGISTRY = {
        "baseline_sma_cross": "execution.strategies.baseline_sma_cross.BaselineSMACross"
    }

    def _load_strategy(self):
        """
        Dynamically loads the strategy class based on the name.
        """
        if self.strategy_name not in self.REGISTRY:
            raise ValueError(f"Strategy '{self.strategy_name}' not found in registry. Available: {list(self.REGISTRY.keys())}")
            
        module_path, class_name = self.REGISTRY[self.strategy_name].rsplit('.', 1)
        
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls(**self.strategy_config)
        except (ImportError, AttributeError) as e:
            raise ImportError(f"Could not load strategy {self.strategy_name}: {e}")

    def generate(self, data):
        """
        Run the strategy on the provided data.
        
        Args:
            data (pd.DataFrame): Normalized price data.
            
        Returns:
            list: List of signal events.
        """
        return self.strategy.calculate(data)
