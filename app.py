import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = 'animes.db'


def init_db():
  conn = sqlite3.connect(DB_FILE)
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas_animes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anime TEXT,
            temporada INTEGER,
            capitulo INTEGER,
            idioma TEXT,
            url_descarga TEXT,
            estado TEXT DEFAULT 'pendiente',
            filecode TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route('/')
def home():
  return jsonify({'status': 'online', 'mensaje': '🚀 API Central Render Activa'})


# 1. Recibir datos desde el navegador en InfinityFree
@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
  try:
    data = request.json or {}
    anime = data.get('anime', 'ONE PIECE')
    temporada = int(data.get('temporada', 1))
    capitulo = int(data.get('capitulo', 1))
    idioma = data.get('idioma', 'Subtitulado')
    url_descarga = data.get('url_descarga')

    print(
        f'📥 [RENDER RECIBIÓ] Anime: {anime} | T{temporada} C{capitulo} | URL:'
        f' {url_descarga}'
    )

    if not url_descarga:
      return jsonify({'error': 'La URL es obligatoria'}), 400

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
            INSERT INTO tareas_animes (anime, temporada, capitulo, idioma, url_descarga, estado)
            VALUES (?, ?, ?, ?, ?, 'pendiente')
        """,
        (anime, temporada, capitulo, idioma, url_descarga),
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    conn.close()

    print(f'✅ [BD RENDER] Tarea guardada con ID: {nuevo_id}')
    return jsonify({'status': 'success', 'id': nuevo_id}), 201
  except Exception as e:
    print(f'❌ [ERROR EN AGREGAR]: {str(e)}')
    return jsonify({'error': str(e)}), 500


# 2. Entregar tarea a Google Colab
@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
  try:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM tareas_animes WHERE estado = 'pendiente' LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
      tarea = dict(row)
      print(f'📤 [COLAB PIDió] Entregando tarea ID {tarea["id"]}: {tarea["anime"]}')
      return jsonify(tarea)

    return jsonify(None)
  except Exception as e:
    print(f'❌ [ERROR EN SIGUIENTE]: {str(e)}')
    return jsonify({'error': str(e)}), 500


# 3. Marcar como completado
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tareas_animes SET estado = 'completado' WHERE id = ?",
        (id_tarea,),
    )
    conn.commit()
    conn.close()
    print(f'🎉 [COMPLETADO] Tarea ID {id_tarea} marcada como procesada.')
    return jsonify({'status': 'success'})
  except Exception as e:
    print(f'❌ [ERROR EN COMPLETAR]: {str(e)}')
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
