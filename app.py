import os
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

COLA_TAREAS = []
CONTADOR_ID = 1

# URL exacta de tu endpoint PHP en InfinityFree
PHP_WEBHOOK_URL = 'https://index.free.je/api_completar.php'


def enviar_resultado_a_php(id_tarea, filecode, url_reproduccion, estado):
    try:
        # El script PHP espera recibir 'id', 'filecode' y 'url_reproduccion'
        payload = {
            'id': id_tarea,
            'filecode': filecode,
            'url_reproduccion': url_reproduccion,
            'estado': estado
        }
        
        # Enviar los datos por POST JSON hacia tu archivo PHP
        response = requests.post(PHP_WEBHOOK_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f'✅ [Enviado a PHP] Tarea ID {id_tarea} guardada en InfinityFree por PHP.')
            print(f'Respuesta PHP: {response.text}')
        else:
            print(f'⚠️ [Aviso PHP] El servidor PHP respondió con estado {response.status_code}: {response.text}')
    except Exception as e:
        print(f'❌ [Error al notificar a PHP]: {e}')


@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mensaje': '🚀 API Central Render Activa (Modo Memoria con Webhook PHP)',
        'pendientes': len(COLA_TAREAS),
    })


@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
    global CONTADOR_ID
    try:
        data = request.json or {}
        anime = data.get('anime', 'ONE PIECE')
        temporada = int(data.get('temporada', 1))
        capitulo = int(data.get('capitulo', 1))
        idioma = data.get('idioma', 'Latino')
        url_descarga = data.get('url_descarga')
        id_mysql = data.get('id', CONTADOR_ID)

        if not url_descarga:
            return jsonify({'error': 'La URL es obligatoria'}), 400

        nueva_tarea = {
            'id': id_mysql,
            'anime': anime,
            'temporada': temporada,
            'capitulo': capitulo,
            'idioma': idioma,
            'url_descarga': url_descarga,
            'estado': 'pendiente',
        }

        COLA_TAREAS.append(nueva_tarea)
        print(
            f'📥 [NUEVA TAREA] ID: {id_mysql} | {anime} T{temporada} C{capitulo}'
        )
        CONTADOR_ID += 1

        return jsonify({'status': 'success', 'id': id_mysql}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
    try:
        for tarea in COLA_TAREAS:
            if tarea['estado'] == 'pendiente':
                return jsonify(tarea)
        return jsonify(None)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
    global COLA_TAREAS
    try:
        data = request.json or {}
        filecode = data.get('filecode', '')
        url_reproduccion = data.get('url_reproduccion', '')
        estado = data.get('estado', 'completado')

        # Notificar a PHP para que sea PHP quien actualice la base de datos MySQL
        enviar_resultado_a_php(id_tarea, filecode, url_reproduccion, estado)

        # Purgar de la memoria de Render
        COLA_TAREAS = [t for t in COLA_TAREAS if t['id'] != id_tarea]
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/estado-global', methods=['GET'])
def estado_global():
    return jsonify({'status': 'success', 'pendientes': len(COLA_TAREAS)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
