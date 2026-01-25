from typing import List, Optional
from datetime import datetime, timezone
from core.interfaces import IBroker, IDataSource, IStrategy
from core.logger import get_logger

# Import the legacy pipeline for transitional bridge
from execution.run_cycle import run_pipeline as legacy_run_pipeline

logger = get_logger("TradingEngine")

class TradingEngine:
    """
    Orchestrates the trading cycle: Data -> Strategy -> Execution.
    
    This is a transitional implementation that wraps the existing run_pipeline
    while providing the new interface-based architecture.
    """
    def __init__(self, broker: Optional[IBroker] = None, 
                 data_source: Optional[IDataSource] = None, 
                 strategy: Optional[IStrategy] = None):
        self.broker = broker
        self.data_source = data_source
        self.strategy = strategy

    def run_cycle(self, symbol: str = None):
        """
        Executes a single trading cycle.
        
        For now, this wraps the legacy run_pipeline function for stability.
        Future versions will use self.broker, self.data_source, self.strategy directly.
        """
        logger.info(f"--- TradingEngine: Starting Cycle ---")
        
        try:
            # Transitional: Call the existing pipeline logic
            legacy_run_pipeline()
            logger.info(f"--- TradingEngine: Cycle Completed ---")
        except Exception as e:
            logger.error(f"TradingEngine Error: {e}", exc_info=True)
            raise
