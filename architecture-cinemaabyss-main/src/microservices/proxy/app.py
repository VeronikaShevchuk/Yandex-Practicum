from flask import Flask, jsonify, request
import requests
import random
import os
import logging
from functools import wraps

app = Flask(__name__)

# Конфигурация
MOVIES_MIGRATION_PERCENT = int(os.getenv('MOVIES_MIGRATION_PERCENT', 0))
MONOLITH_URL = os.getenv('MONOLITH_URL', 'http://monolith:8080')
MOVIES_SERVICE_URL = os.getenv('MOVIES_SERVICE_URL', 'http://movies-service:8081')
PORT = os.getenv('PORT', '8000')

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def should_use_new_movies_service():
    """Определяет, использовать ли новый сервис фильмов на основе процента миграции"""
    return random.randint(1, 100) <= MOVIES_MIGRATION_PERCENT

def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return jsonify({'error': 'Service unavailable'}), 503
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function

def proxy_request(target_url, method='GET', data=None):
    """Проксирует запрос к целевому сервису"""
    headers = {key: value for key, value in request.headers if key.lower() != 'host'}
    
    if method == 'GET':
        response = requests.get(target_url, params=request.args, headers=headers)
    elif method == 'POST':
        response = requests.post(target_url, json=data or request.get_json(), headers=headers)
    else:
        return jsonify({'error': 'Method not supported'}), 405
    
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'proxy'})

# Movies endpoints with feature flag
@app.route('/api/movies', methods=['GET', 'POST'])
@handle_errors
def movies_proxy():
    """Прокси для эндпоинтов movies с feature flag"""
    use_new = should_use_new_movies_service()
    
    if use_new:
        target_url = f"{MOVIES_SERVICE_URL}/api/movies"
        service_name = "movies-service"
    else:
        target_url = f"{MONOLITH_URL}/api/movies" 
        service_name = "monolith"
    
    logger.info(f"Routing movies request to {service_name}: {target_url}")
    
    response = proxy_request(target_url, request.method, request.get_json())
    
    # Для GET запросов возвращаем данные как есть
    if request.method == 'GET':
        return jsonify(response.json()), response.status_code
    else:
        # Для POST добавляем информацию о источнике
        result = response.json()
        result['source_service'] = service_name
        result['migration_percent'] = MOVIES_MIGRATION_PERCENT
        return jsonify(result), response.status_code

# All other endpoints go to monolith
@app.route('/api/users', methods=['GET', 'POST'])
@handle_errors
def users_proxy():
    """Прокси для эндпоинтов users"""
    target_url = f"{MONOLITH_URL}/api/users"
    logger.info(f"Routing users request to monolith: {target_url}")
    
    response = proxy_request(target_url, request.method, request.get_json())
    return jsonify(response.json()), response.status_code

@app.route('/api/payments', methods=['GET', 'POST'])
@handle_errors
def payments_proxy():
    """Прокси для эндпоинтов payments"""
    target_url = f"{MONOLITH_URL}/api/payments"
    logger.info(f"Routing payments request to monolith: {target_url}")
    
    response = proxy_request(target_url, request.method, request.get_json())
    return jsonify(response.json()), response.status_code

@app.route('/api/subscriptions', methods=['GET', 'POST'])
@handle_errors
def subscriptions_proxy():
    """Прокси для эндпоинтов subscriptions"""
    target_url = f"{MONOLITH_URL}/api/subscriptions"
    logger.info(f"Routing subscriptions request to monolith: {target_url}")
    
    response = proxy_request(target_url, request.method, request.get_json())
    return jsonify(response.json()), response.status_code

# Catch-all for other API routes
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@handle_errors
def catch_all_proxy(path):
    """Прокси для всех остальных API эндпоинтов"""
    target_url = f"{MONOLITH_URL}/api/{path}"
    logger.info(f"Routing request to monolith: {target_url}")
    
    response = proxy_request(target_url, request.method, request.get_json())
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    logger.info(f"Starting Proxy Service on port {PORT}")
    logger.info(f"Movies migration percent: {MOVIES_MIGRATION_PERCENT}%")
    logger.info(f"Monolith URL: {MONOLITH_URL}")
    logger.info(f"Movies Service URL: {MOVIES_SERVICE_URL}")
    
    app.run(host='0.0.0.0', port=PORT, debug=False)