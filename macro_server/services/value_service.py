from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..repositories import value_repo, indicator_repo
from ..schemas import models as schemas

class MacroValueService:
    def __init__(self, db: Session):
        self.db = db

    def create_value(self, value: schemas.MacroValueCreate):
        indicator = indicator_repo.get_indicator(self.db, value.indicator_id)
        if not indicator:
            raise HTTPException(status_code=404, detail="Indicator not found")
        return value_repo.create_value(self.db, value)

    def get_values(self, indicator_id: int):
        # We could add more logic here, e.g. filtering by date range
        return value_repo.get_values_by_indicator(self.db, indicator_id)
