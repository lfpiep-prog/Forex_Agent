from sqlalchemy.orm import Session
from .. import models
from ..schemas import models as schemas

def create_value(db: Session, value: schemas.MacroValueCreate):
    db_value = models.MacroValue(
        indicator_id=value.indicator_id,
        date=value.date,
        value=value.value,
        is_forecast=value.is_forecast
    )
    db.add(db_value)
    db.commit()
    db.refresh(db_value)
    return db_value

def get_values_by_indicator(db: Session, indicator_id: int):
    return db.query(models.MacroValue).filter(models.MacroValue.indicator_id == indicator_id).order_by(models.MacroValue.date.desc()).all()
