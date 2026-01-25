from sqlalchemy.orm import Session
from fastapi import HTTPException
from repositories import indicator_repo
from schemas import models as schemas

class IndicatorService:
    def __init__(self, db: Session):
        self.db = db

    def create_indicator(self, indicator: schemas.IndicatorCreate):
        existing = indicator_repo.get_indicator_by_name(self.db, indicator.name)
        if existing:
            raise HTTPException(status_code=400, detail="Indicator already exists")
        return indicator_repo.create_indicator(self.db, indicator)

    def get_indicators(self, skip: int = 0, limit: int = 100):
        return indicator_repo.get_indicators(self.db, skip, limit)
