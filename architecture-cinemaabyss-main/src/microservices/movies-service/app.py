from flask import Flask, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage for movies
movies = [
    {
        'id': 1,
        'title': 'Inception',
        'description': 'A thief who steals corporate secrets through dream-sharing technology.',
        'genres': ['Sci-Fi', 'Action', 'Thriller'],
        'rating': 8.8,
        'year': 2010,
        'director': 'Christopher Nolan'
    },
    {
        'id': 2, 
        'title': 'The Shawshank Redemption',
        'description': 'Two imprisoned men bond over a number of years.',
        'genres': ['Drama'],
        'rating': 9.3,
        'year': 1994,
        'director': 'Frank Darabont'
    }
]

@app.route('/api/movies/health', methods=['GET'])
def health_check():
    return jsonify({'status': True, 'service': 'movies-microservice'})

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
            'year': data.get('year', 2023),
            'director': data.get('director', 'Unknown'),
            'created_at': datetime.now().isoformat()
        }
        movies.append(new_movie)
        return jsonify(new_movie), 201

if __name__ == '__main__':
    print("Starting Movies Microservice on port 8081")
    app.run(host='0.0.0.0', port=8081, debug=False)