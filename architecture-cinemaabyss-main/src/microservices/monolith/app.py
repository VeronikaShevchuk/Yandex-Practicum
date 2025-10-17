from flask import Flask, jsonify, request
import random
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage for demo
users = []
movies = []
payments = []
subscriptions = []

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'monolith'})

# Users endpoints
@app.route('/api/users', methods=['GET', 'POST'])
def users_handler():
    if request.method == 'GET':
        user_id = request.args.get('id')
        if user_id:
            user = next((u for u in users if u['id'] == int(user_id)), None)
            if user:
                return jsonify(user)
            return jsonify({'error': 'User not found'}), 404
        return jsonify(users)
    
    elif request.method == 'POST':
        data = request.get_json()
        new_user = {
            'id': len(users) + 1,
            'username': data.get('username', f'user{len(users) + 1}'),
            'email': data.get('email', f'user{len(users) + 1}@example.com'),
            'created_at': datetime.now().isoformat()
        }
        users.append(new_user)
        return jsonify(new_user), 201

# Movies endpoints
@app.route('/api/movies', methods=['GET', 'POST'])
def movies_handler():
    if request.method == 'GET':
        movie_id = request.args.get('id')
        if movie_id:
            movie = next((m for m in movies if m['id'] == int(movie_id)), None)
            if movie:
                return jsonify(movie)
            return jsonify({'error': 'Movie not found'}), 404
        return jsonify(movies)
    
    elif request.method == 'POST':
        data = request.get_json()
        new_movie = {
            'id': len(movies) + 1,
            'title': data.get('title', f'Movie {len(movies) + 1}'),
            'description': data.get('description', 'No description'),
            'genres': data.get('genres', []),
            'rating': data.get('rating', 0.0),
            'created_at': datetime.now().isoformat()
        }
        movies.append(new_movie)
        return jsonify(new_movie), 201

# Payments endpoints
@app.route('/api/payments', methods=['GET', 'POST'])
def payments_handler():
    if request.method == 'GET':
        payment_id = request.args.get('id')
        if payment_id:
            payment = next((p for p in payments if p['id'] == int(payment_id)), None)
            if payment:
                return jsonify(payment)
            return jsonify({'error': 'Payment not found'}), 404
        return jsonify(payments)
    
    elif request.method == 'POST':
        data = request.get_json()
        new_payment = {
            'id': len(payments) + 1,
            'user_id': data.get('user_id'),
            'amount': data.get('amount', 0.0),
            'status': 'completed',
            'created_at': datetime.now().isoformat()
        }
        payments.append(new_payment)
        return jsonify(new_payment), 201

# Subscriptions endpoints
@app.route('/api/subscriptions', methods=['GET', 'POST'])
def subscriptions_handler():
    if request.method == 'GET':
        subscription_id = request.args.get('id')
        if subscription_id:
            subscription = next((s for s in subscriptions if s['id'] == int(subscription_id)), None)
            if subscription:
                return jsonify(subscription)
            return jsonify({'error': 'Subscription not found'}), 404
        return jsonify(subscriptions)
    
    elif request.method == 'POST':
        data = request.get_json()
        new_subscription = {
            'id': len(subscriptions) + 1,
            'user_id': data.get('user_id'),
            'plan_type': data.get('plan_type', 'premium'),
            'start_date': data.get('start_date', datetime.now().isoformat()),
            'end_date': data.get('end_date', datetime.now().isoformat()),
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        subscriptions.append(new_subscription)
        return jsonify(new_subscription), 201

if __name__ == '__main__':
    
    users.append({'id': 1, 'username': 'demo_user', 'email': 'demo@example.com'})
    movies.append({
        'id': 1, 
        'title': 'Demo Movie', 
        'description': 'A demo movie for testing',
        'genres': ['Action', 'Drama'],
        'rating': 4.5
    })
    
    print("Starting Monolith Service on port 8080")
    app.run(host='0.0.0.0', port=8080, debug=False)