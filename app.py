import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista en memoria robusta para evitar pérdida de datos en el plan gratuito de Render
COLA_TAREAS = []
CONTADOR_ID = 1


@app.route('/')
def home():
  return jsonify({
      'status': 'online',
      'mensaje': '🚀 API Central Render Activa',
      'pendientes': len(COLA_TAREAS),
  })


# 1. Recibir datos desde el navegador en InfinityFree
@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
  global CONTADOR_ID
  try:
    data = request.json or {}
    anime = data.get('anime', 'ONE PIECE')
    temporada = int(data.get('temporada', 1))
    capitulo = int(data.get('capitulo', 1))
    idioma = data.get('idioma', 'Subtitulado')
    url_descarga = data.get('url_descarga')

    if not url_descarga:
      return jsonify({'error': 'La URL es obligatoria'}), 400

    # Verificar si ya existe en la cola para evitar duplicados exactos
    for t in COLA_TAREAS:
      if (
          t['anime'] == anime
          and t['temporada'] == temporada
          and t['capitulo'] == capitulo
          and t['idioma'] == idioma
      ):
        t['url_descarga'] = url_descarga
        t['estado'] = 'pendiente'
        print(
            f'🔄 [ACTUALIZADO] Tarea ID {t["id"]} actualizada con nueva URL.'
        )
        return jsonify(
            {'status': 'success', 'id': t['id'], 'mensaje': 'Actualizado'}
        ), 200

    nueva_tarea = {
        'id': CONTADOR_ID,
        'anime': anime,
        'temporada': temporada,
        'capitulo': capitulo,
        'idioma': idioma,
        'url_descarga': url_descarga,
        'estado': 'pendiente',
    }

    COLA_TAREAS.append(nueva_tarea)
    print(
        f'📥 [NUEVA TAREA] ID: {CONTADOR_ID} | {anime} T{temporada} C{capitulo}'
        f' | URL: {url_descarga}'
    )
    CONTADOR_ID += 1

    return jsonify(
        {'status': 'success', 'id': nueva_tarea['id'], 'mensaje': 'Agregado'}
    ), 201
  except Exception as e:
    print(f'❌ [ERROR EN AGREGAR]: {str(e)}')
    return jsonify({'error': str(e)}), 500


# 2. Entregar estrictamente la PRIMERA tarea pendiente a Google Colab
@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
  try:
    for tarea in COLA_TAREAS:
      if tarea['estado'] == 'pendiente':
        print(
            f'📤 [COLAB ATENDIDO] Entregando tarea ID {tarea["id"]}:'
            f' {tarea["anime"]} T{tarea["temporada"]} C{tarea["capitulo"]}'
        )
        return jsonify(tarea)

    return jsonify(None)
  except Exception as e:
    print(f'❌ [ERROR EN SIGUIENTE]: {str(e)}')
    return jsonify({'error': str(e)}), 500


# 3. Eliminar o marcar como completado para pasar AUTOMÁTICAMENTE al siguiente
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  global COLA_TAREAS
  try:
    # Purga la tarea de la lista para limpiar el espacio y avanzar al siguiente
    COLA_TAREAS = [t for t in COLA_TAREAS if t['id'] != id_tarea]
    print(
        f'🎉 [COMPLETADO Y PURGADO] Tarea ID {id_tarea} eliminada de la cola.'
        f' Restantes: {len(COLA_TAREAS)}'
    )
    return jsonify({'status': 'success'})
  except Exception as e:
    print(f'❌ [ERROR EN COMPLETAR]: {str(e)}')
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
