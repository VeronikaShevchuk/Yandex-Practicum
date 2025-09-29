from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # temperature, humidity, pressure, etc.
    location = Column(String, nullable=False)
    unit = Column(String, nullable=False)  # °C, %, hPa, etc.
    value = Column(Float, nullable=False)
    status = Column(String, default="active")  # active, inactive, error
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)