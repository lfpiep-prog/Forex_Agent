from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.indicator_service import IndicatorService
from schemas import models as schemas
from schemas.common import StandardResponse, Meta

router = APIRouter(prefix="/indicators", tags=["indicators"])

@router.post("/", response_model=StandardResponse[schemas.Indicator])
def create_indicator(indicator: schemas.IndicatorCreate, db: Session = Depends(get_db)):
    service = IndicatorService(db)
    new_indicator = service.create_indicator(indicator)
    return StandardResponse(data=new_indicator)

@router.get("/", response_model=StandardResponse[List[schemas.Indicator]])
def read_indicators(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = IndicatorService(db)
    indicators = service.get_indicators(skip, limit)
    return StandardResponse(
        data=indicators,
        meta=Meta(limit=limit, page=(skip // limit) + 1)
    )
