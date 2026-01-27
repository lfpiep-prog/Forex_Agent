from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class Meta(BaseModel):
    page: int = 1
    limit: int = 100
    total: Optional[int] = None

class StandardResponse(GenericModel, Generic[T]):
    data: T
    meta: Optional[Meta] = None
    error: Optional[str] = None
