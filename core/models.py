from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from core.database import Base
from core.signals import SignalType


class TradeResult(Base):
    """
    Persisted record of an executed trade.
    """
    __tablename__ = "trade_results"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # LONG, SHORT
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)  # Null until closed
    quantity = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)  # Null until closed
    status = Column(String(20), default="OPEN", nullable=False)  # OPEN, CLOSED, CANCELLED
    broker_order_id = Column(String(100), nullable=True)
    rationale = Column(String(500), nullable=True)
    
    def __repr__(self):
        return f"<TradeResult(id={self.id}, symbol={self.symbol}, direction={self.direction}, status={self.status})>"
