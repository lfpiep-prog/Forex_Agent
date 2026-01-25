from sqlalchemy.orm import Session
import models
from schemas import models as schemas

def get_indicator_by_name(db: Session, name: str):
    return db.query(models.Indicator).filter(models.Indicator.name == name).first()

def get_indicator(db: Session, indicator_id: int):
    return db.query(models.Indicator).filter(models.Indicator.id == indicator_id).first()

def get_indicators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Indicator).offset(skip).limit(limit).all()

def create_indicator(db: Session, indicator: schemas.IndicatorCreate):
    db_indicator = models.Indicator(
        name=indicator.name,
        description=indicator.description,
        country=indicator.country,
        frequency=indicator.frequency,
        source=indicator.source
    )
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator
