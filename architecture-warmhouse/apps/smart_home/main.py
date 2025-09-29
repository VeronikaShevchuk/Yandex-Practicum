from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import random
from datetime import datetime
from . import models, schemas, database
from .database import SessionLocal, engine

# Создание таблиц
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Home Sensor API",
    description="API для управления датчиками умного дома",
    version="1.0.0"
)

# Dependency для получения сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "service": "smart-home-sensor-api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }

@app.get("/api/v1/sensors", response_model=List[schemas.SensorResponse])
async def get_all_sensors(db: Session = Depends(get_db)):
    """Получить все датчики"""
    sensors = db.query(models.Sensor).all()
    
    # Обновляем значения для каждого датчика (имитация новых показаний)
    for sensor in sensors:
        # Генерируем случайное значение температуры в зависимости от типа датчика
        if sensor.type == "temperature":
            new_value = round(random.uniform(18.0, 25.0), 1)
        elif sensor.type == "humidity":
            new_value = round(random.uniform(30.0, 70.0), 1)
        elif sensor.type == "pressure":
            new_value = round(random.uniform(980.0, 1020.0), 1)
        else:
            new_value = round(random.uniform(0.0, 100.0), 1)
        
        sensor.value = new_value
        sensor.last_updated = datetime.utcnow()
    
    db.commit()
    return sensors

@app.get("/api/v1/sensors/{sensor_id}", response_model=schemas.SensorResponse)
async def get_sensor_by_id(sensor_id: int, db: Session = Depends(get_db)):
    """Получить датчик по ID"""
    sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Датчик не найден")
    
    # Обновляем значение (имитация новых показаний)
    if sensor.type == "temperature":
        new_value = round(random.uniform(18.0, 25.0), 1)
    elif sensor.type == "humidity":
        new_value = round(random.uniform(30.0, 70.0), 1)
    elif sensor.type == "pressure":
        new_value = round(random.uniform(980.0, 1020.0), 1)
    else:
        new_value = round(random.uniform(0.0, 100.0), 1)
    
    sensor.value = new_value
    sensor.last_updated = datetime.utcnow()
    db.commit()
    
    return sensor

@app.post("/api/v1/sensors", response_model=schemas.SensorResponse)
async def create_sensor(sensor: schemas.SensorCreate, db: Session = Depends(get_db)):
    """Создать новый датчик"""
    # Генерируем начальное значение в зависимости от типа
    if sensor.type == "temperature":
        initial_value = round(random.uniform(18.0, 25.0), 1)
    elif sensor.type == "humidity":
        initial_value = round(random.uniform(30.0, 70.0), 1)
    elif sensor.type == "pressure":
        initial_value = round(random.uniform(980.0, 1020.0), 1)
    else:
        initial_value = round(random.uniform(0.0, 100.0), 1)
    
    db_sensor = models.Sensor(
        name=sensor.name,
        type=sensor.type,
        location=sensor.location,
        unit=sensor.unit,
        value=initial_value,
        status="active",
        last_updated=datetime.utcnow()
    )
    
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor

@app.put("/api/v1/sensors/{sensor_id}", response_model=schemas.SensorResponse)
async def update_sensor(sensor_id: int, sensor_update: schemas.SensorUpdate, db: Session = Depends(get_db)):
    """Обновить информацию о датчике"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Датчик не найден")
    
    # Обновляем поля
    for field, value in sensor_update.dict(exclude_unset=True).items():
        setattr(db_sensor, field, value)
    
    db_sensor.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor

@app.delete("/api/v1/sensors/{sensor_id}")
async def delete_sensor(sensor_id: int, db: Session = Depends(get_db)):
    """Удалить датчик"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Датчик не найден")
    
    db.delete(db_sensor)
    db.commit()
    
    return {"message": "Датчик успешно удален", "sensor_id": sensor_id}

@app.patch("/api/v1/sensors/{sensor_id}/value", response_model=schemas.SensorResponse)
async def update_sensor_value(sensor_id: int, value_update: schemas.SensorValueUpdate, db: Session = Depends(get_db)):
    """Обновить значение и статус датчика"""
    db_sensor = db.query(models.Sensor).filter(models.Sensor.id == sensor_id).first()
    if not db_sensor:
        raise HTTPException(status_code=404, detail="Датчик не найден")
    
    # Обновляем значение и статус
    if value_update.value is not None:
        db_sensor.value = value_update.value
    
    if value_update.status is not None:
        db_sensor.status = value_update.status
    
    db_sensor.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_sensor)
    
    return db_sensor

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)