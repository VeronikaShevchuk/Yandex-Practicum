from flask import Flask, jsonify, request
from kafka import KafkaProducer, KafkaConsumer
import json
import threading
import logging
import os
import time
from datetime import datetime

app = Flask(__name__)

# Конфигурация для Kubernetes
KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'kafka.cinemaabyss.svc.cluster.local:9092')
PORT = os.getenv('PORT', '8082')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для Kafka компонентов
producer = None
consumer_thread = None

def init_kafka():
    """Инициализация Kafka producer с retry логикой"""
    global producer
    max_retries = 5
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to Kafka at {KAFKA_BROKER} (attempt {attempt + 1}/{max_retries})")
            
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                request_timeout_ms=30000,
                metadata_max_age_ms=30000
            )
            
            # Test connection
            producer.send('test-connection', {'test': True})
            producer.flush(timeout=10)
            logger.info("Successfully connected to Kafka")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All connection attempts failed")
                return False

def start_kafka_consumer():
    """Запуск Kafka consumer в отдельном потоке"""
    def consume_messages():
        try:
            consumer = KafkaConsumer(
                'user-events',
                'payment-events', 
                'movie-events',
                bootstrap_servers=[KAFKA_BROKER],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')) if m else None,
                group_id='events-service-group',
                auto_offset_reset='earliest',
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )
            
            logger.info("Kafka consumer started successfully")
            
            for message in consumer:
                if message.value:
                    logger.info(f"Received message: topic={message.topic}, partition={message.partition}, offset={message.offset}")
                    logger.info(f"Message value: {message.value}")
                else:
                    logger.warning("Received empty message")
                    
        except Exception as e:
            logger.error(f"Kafka consumer error: {str(e)}")
    
    global consumer_thread
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)
    consumer_thread.start()

@app.before_first_request
def startup():
    """Инициализация при старте приложения"""
    logger.info("Starting Events Service initialization...")
    if init_kafka():
        start_kafka_consumer()
    else:
        logger.error("Kafka initialization failed - events will not be processed")

@app.route('/api/events/health', methods=['GET'])
def health_check():
    kafka_status = "connected" if producer else "disconnected"
    return jsonify({
        'status': True, 
        'service': 'events-microservice',
        'kafka': kafka_status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/events/user', methods=['POST'])
def create_user_event():
    """Создание события пользователя"""
    if not producer:
        return jsonify({'error': 'Kafka not available'}), 503
    
    data = request.get_json()
    
    event = {
        'type': 'user',
        'event': data.get('action', 'user_created'),
        'user_id': data.get('user_id'),
        'username': data.get('username'),
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    try:
        future = producer.send('user-events', event)
        # Wait for confirmation
        result = future.get(timeout=10)
        logger.info(f"User event sent successfully: topic={result.topic}, partition={result.partition}, offset={result.offset}")
        
        return jsonify({
            'status': 'success',
            'message': 'User event created',
            'event': event,
            'kafka_info': {
                'topic': 'user-events',
                'partition': result.partition,
                'offset': result.offset
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to send user event: {str(e)}")
        return jsonify({'error': 'Failed to send event to Kafka'}), 500

@app.route('/api/events/payment', methods=['POST'])
def create_payment_event():
    """Создание платежного события"""
    if not producer:
        return jsonify({'error': 'Kafka not available'}), 503
    
    data = request.get_json()
    
    event = {
        'type': 'payment',
        'event': 'payment_processed',
        'payment_id': data.get('payment_id'),
        'user_id': data.get('user_id'),
        'amount': data.get('amount'),
        'status': data.get('status', 'completed'),
        'method_type': data.get('method_type', 'credit_card'),
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    try:
        future = producer.send('payment-events', event)
        result = future.get(timeout=10)
        logger.info(f"Payment event sent successfully: topic={result.topic}, partition={result.partition}, offset={result.offset}")
        
        return jsonify({
            'status': 'success',
            'message': 'Payment event created',
            'event': event,
            'kafka_info': {
                'topic': 'payment-events',
                'partition': result.partition,
                'offset': result.offset
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to send payment event: {str(e)}")
        return jsonify({'error': 'Failed to send event to Kafka'}), 500

@app.route('/api/events/movie', methods=['POST'])
def create_movie_event():
    """Создание события фильма"""
    if not producer:
        return jsonify({'error': 'Kafka not available'}), 503
    
    data = request.get_json()
    
    event = {
        'type': 'movie',
        'event': data.get('action', 'movie_viewed'),
        'user_id': data.get('user_id'),
        'movie_id': data.get('movie_id'),
        'title': data.get('title'),
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    try:
        future = producer.send('movie-events', event)
        result = future.get(timeout=10)
        logger.info(f"Movie event sent successfully: topic={result.topic}, partition={result.partition}, offset={result.offset}")
        
        return jsonify({
            'status': 'success',
            'message': 'Movie event created',
            'event': event,
            'kafka_info': {
                'topic': 'movie-events',
                'partition': result.partition,
                'offset': result.offset
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Failed to send movie event: {str(e)}")
        return jsonify({'error': 'Failed to send event to Kafka'}), 500

# Эндпоинт для тестирования всех типов событий
@app.route('/api/events/test', methods=['POST'])
def test_all_events():
    """Тестовый эндпоинт для создания всех типов событий"""
    test_data = request.get_json() or {
        'user_id': 123,
        'movie_id': 456,
        'payment_id': 789
    }
    
    results = []
    
    # Test user event
    user_response = create_user_event()
    results.append({
        'type': 'user',
        'status_code': user_response[1],
        'response': user_response[0].get_json() if user_response[0] else None
    })
    
    # Test payment event  
    payment_response = create_payment_event()
    results.append({
        'type': 'payment',
        'status_code': payment_response[1],
        'response': payment_response[0].get_json() if payment_response[0] else None
    })
    
    # Test movie event
    movie_response = create_movie_event()
    results.append({
        'type': 'movie', 
        'status_code': movie_response[1],
        'response': movie_response[0].get_json() if movie_response[0] else None
    })
    
    return jsonify({'test_results': results})

if __name__ == '__main__':
    logger.info(f"Starting Events Microservice on port {PORT}")
    logger.info(f"Kafka broker: {KAFKA_BROKER}")
    app.run(host='0.0.0.0', port=PORT, debug=False)