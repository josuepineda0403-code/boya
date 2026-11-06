import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PHP_SIGUIENTE_URL = 'https://index.free.je/api_siguiente.php'
PHP_COMPLETAR_URL = 'https://index.free.je/api_completar.php'

@app.route('/')
def home():
    return jsonify({'status': 'online', 'mensaje': '🚀 API Central Render Sincronizada con PHP'})

@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(PHP_SIGUIENTE_URL, headers=headers, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': f'PHP respondió con estado {response.status_code}'}), 500

        data = response.json()
        if data.get('has_task') and data.get('tarea'):
            return jsonify(data['tarea'])
        
        return jsonify(None)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
    try:
        data = request.json or {}
        payload = {
            'id': id_tarea,
            'filecode': data.get('filecode', ''),
            'url_reproduccion': data.get('url_reproduccion', ''),
            'estado': data.get('estado', 'completado')
        }
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.post(PHP_COMPLETAR_URL, json=payload, headers=headers, timeout=15)
        
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
