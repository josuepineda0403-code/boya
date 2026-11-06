import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# URLs de tus endpoints PHP oficiales en InfinityFree
PHP_SIGUIENTE_URL = 'https://index.free.je/api_siguiente.php'
PHP_COMPLETAR_URL = 'https://index.free.je/api_completar.php'


@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mensaje': '🚀 API Central Render Activa (Sincronizada con PHP InfinityFree)',
    })


@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
    try:
        # Consultamos directamente a tu api_siguiente.php para que maneje el FOR UPDATE y el bloqueo seguro
        response = requests.get(PHP_SIGUIENTE_URL, timeout=15)
        data = response.json()

        # Si PHP responde con una tarea válida
        if data.get('has_task') and data.get('tarea'):
            tarea = data['tarea']
            
            # Opcional: Si quieres agregar rastreo inteligente para buscar el filecode anterior
            # puedes hacerlo consultando una función o pasándolo directamente desde PHP.
            # Por ahora, devolvemos la tarea exacta que preparó tu api_siguiente.php
            return jsonify(tarea)
        
        # Si la cola está vacía
        return jsonify(None)

    except Exception as e:
        print(f"❌ Error al conectar con api_siguiente.php: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
    try:
        data = request.json or {}
        filecode = data.get('filecode', '')
        url_reproduccion = data.get('url_reproduccion', '')
        estado = data.get('estado', 'completado')

        # Empaquetar los datos para enviarlos a tu api_completar.php existente
        payload = {
            'id': id_tarea,
            'filecode': filecode,
            'url_reproduccion': url_reproduccion,
            'estado': estado
        }

        # Enviar los datos por POST a tu PHP para que actualice la base de datos definitivamente
        response = requests.post(PHP_COMPLETAR_URL, json=payload, timeout=15)
        print(f'📡 [Respuesta de api_completar.php]: {response.text}')

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"❌ Error al notificar a api_completar.php: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
