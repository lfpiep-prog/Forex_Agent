from typing import Optional, List
from datetime import date
from pydantic import BaseModel

class IndicatorBase(BaseModel):
    name: str
    description: Optional[str] = None
    country: str
    frequency: str
    source: Optional[str] = None

class IndicatorCreate(IndicatorBase):
    pass

class Indicator(IndicatorBase):
    id: int
    class Config:
        orm_mode = True

class MacroValueBase(BaseModel):
    date: date
    value: float
    is_forecast: bool = False

class MacroValueCreate(MacroValueBase):
    indicator_id: int

class MacroValue(MacroValueBase):
    id: int
    indicator_id: int
    class Config:
        orm_mode = True
