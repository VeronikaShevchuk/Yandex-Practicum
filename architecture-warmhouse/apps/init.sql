-- Создание таблицы датчиков
CREATE TABLE IF NOT EXISTS sensors (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    location VARCHAR(255) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_sensors_location ON sensors(location);
CREATE INDEX IF NOT EXISTS idx_sensors_type ON sensors(type);
CREATE INDEX IF NOT EXISTS idx_sensors_status ON sensors(status);
CREATE INDEX IF NOT EXISTS idx_sensors_last_updated ON sensors(last_updated);

-- Вставка тестовых данных
INSERT INTO sensors (name, type, location, unit, value, status) VALUES
('Гостиная температура', 'temperature', 'Living Room', '°C', 22.5, 'active'),
('Спальня влажность', 'humidity', 'Bedroom', '%', 45.0, 'active'),
('Кухня давление', 'pressure', 'Kitchen', 'hPa', 1013.25, 'active'),
('Прихожая температура', 'temperature', 'Hallway', '°C', 20.8, 'active'),
('Ванная влажность', 'humidity', 'Bathroom', '%', 65.2, 'active')
ON CONFLICT DO NOTHING;