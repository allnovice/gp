
from flask import Flask, request, jsonify, send_from_directory
from threading import Lock
import os
import time

app = Flask(__name__)
locations = {}
lock = Lock()
BASE = os.path.dirname(os.path.abspath(__file__))
EXPIRY = 60

@app.route('/')
def home():
    return send_from_directory(BASE, 'index.html')

@app.route('/locations', methods=['GET'])
def get_locations():
    now = time.time()
    with lock:
        expired = [
            uid for uid, loc in locations.items()
            if now - loc['updated'] > EXPIRY
        ]
        for uid in expired:
            del locations[uid]

        return jsonify({
            uid: {'lat': loc['lat'], 'lon': loc['lon']}
            for uid, loc in locations.items()
        })

@app.route('/locations', methods=['POST'])
def update_location():
    data = request.get_json(silent=True) or {}
    uid = str(data.get('id', '')).strip()

    if not uid or 'lat' not in data or 'lon' not in data:
        return jsonify({'error': 'id, lat and lon required'}), 400

    with lock:
        locations[uid] = {
            'lat': data['lat'],
            'lon': data['lon'],
            'updated': time.time()
        }

    return jsonify({'ok': True})

@app.route('/locations/<uid>', methods=['DELETE'])
def delete_location(uid):
    with lock:
        locations.pop(uid, None)
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8081)

