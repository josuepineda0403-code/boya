import os
import pymysql
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

COLA_TAREAS = []
CONTADOR_ID = 1

# Configuración de tu MySQL en InfinityFree para actualización automática
DB_HOST = 'sql107.infinityfree.com'
DB_USER = 'if0_43337662'
DB_PASS = 'Siempresolo12'
DB_NAME = 'if0_43337662_gestor_animes'


def actualizar_mysql_completado(id_tarea, filecode, url_reproduccion):
  try:
    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
    )
    with connection.cursor() as cursor:
      sql = """
                UPDATE cola_tareas 
                SET estado = 'completado', filecode = %s, url_reproduccion = %s 
                WHERE id = %s
            """
      cursor.execute(sql, (filecode, url_reproduccion, id_tarea))
      connection.commit()
    connection.close()
    print(
        f'✅ [MySQL Actualizado] Tarea ID {id_tarea} marcada como completada en'
        ' InfinityFree.'
    )
  except Exception as e:
    print(f'❌ [Error MySQL Remoto]: {e}')


@app.route('/')
def home():
  return jsonify({
      'status': 'online',
      'mensaje': '🚀 API Central Render Activa',
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

    # Actualizar directamente en la base de datos MySQL del usuario
    actualizar_mysql_completado(id_tarea, filecode, url_reproduccion)

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
