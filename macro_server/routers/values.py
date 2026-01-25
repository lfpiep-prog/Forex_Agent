from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.value_service import MacroValueService
from schemas import models as schemas
from schemas.common import StandardResponse

router = APIRouter(prefix="/values", tags=["values"])

@router.post("/", response_model=StandardResponse[schemas.MacroValue])
def create_value(value: schemas.MacroValueCreate, db: Session = Depends(get_db)):
    service = MacroValueService(db)
    new_value = service.create_value(value)
    return StandardResponse(data=new_value)

@router.get("/{indicator_id}", response_model=StandardResponse[List[schemas.MacroValue]])
def read_values(indicator_id: int, db: Session = Depends(get_db)):
    service = MacroValueService(db)
    values = service.get_values(indicator_id)
    return StandardResponse(data=values)
