from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SensorBase(BaseModel):
    name: str
    type: str
    location: str
    unit: str

class SensorCreate(SensorBase):
    pass

class SensorUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    location: Optional[str] = None
    unit: Optional[str] = None
    status: Optional[str] = None

class SensorValueUpdate(BaseModel):
    value: Optional[float] = None
    status: Optional[str] = None

class SensorResponse(SensorBase):
    id: int
    value: float
    status: str
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True