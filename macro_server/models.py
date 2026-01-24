from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # e.g., "GDP_US", "CPI_EU"
    description = Column(String, nullable=True)
    country = Column(String, index=True) # "US", "EU", "JP"
    frequency = Column(String) # "Monthly", "Quarterly", "Daily"
    source = Column(String, nullable=True) # "FRED", "ECB", etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    values = relationship("MacroValue", back_populates="indicator")

class MacroValue(Base):
    __tablename__ = "macro_values"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"))
    date = Column(Date, index=True)
    value = Column(Float)
    is_forecast = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    indicator = relationship("Indicator", back_populates="values")
