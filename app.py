import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Memoria temporal o almacenamiento central en la API de Render
COLA_TAREAS = []
CONTADOR_ID = 1

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mensaje': '🚀 API Central Render Activa (Modo Seguro Unidireccional)',
        'pendientes': len([t for t in COLA_TAREAS if t['estado'] == 'pendiente'])
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

        if not url_descarga:
            return jsonify({'error': 'La URL es obligatoria'}), 400

        nueva_tarea = {
            'id': CONTADOR_ID,
            'anime': anime,
            'temporada': temporada,
            'capitulo': capitulo,
            'idioma': idioma,
            'url_descarga': url_descarga,
            'estado': 'pendiente',
            'filecode': None,
            'url_reproduccion': None
        }

        COLA_TAREAS.append(nueva_tarea)
        print(f'📥 [NUEVA TAREA] ID: {CONTADOR_ID} | {anime} T{temporada} C{capitulo}')
        CONTADOR_ID += 1

        return jsonify({'status': 'success', 'id': nueva_tarea['id']}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
    try:
        for tarea in COLA_TAREAS:
            if tarea['estado'] == 'pendiente':
                tarea['estado'] = 'procesando' # Marcar como en proceso
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

        for tarea in COLA_TAREAS:
            if tarea['id'] == id_tarea:
                tarea['filecode'] = filecode
                tarea['url_reproduccion'] = url_reproduccion
                tarea['estado'] = 'completado_pend_sinc' # Listo para que PHP lo recoja
                print(f'✅ [PROCESADO] Tarea ID {id_tarea} lista para sincronizar con PHP.')
                return jsonify({'status': 'success'})

        return jsonify({'error': 'Tarea no encontrada'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint para que PHP recoja los completados y los guarde en su MySQL local
@app.route('/api/sincronizar-pendientes', methods=['GET'])
def sincronizar_pendientes():
    completados = [t for t in COLA_TAREAS if t['estado'] == 'completado_pend_sinc']
    return jsonify(completados)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
