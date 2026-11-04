import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite que InfinityFree hable con Render sin restricciones de CORS

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


# 1. Recibir datos desde el panel web de InfinityFree (vía JavaScript del navegador)
@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
  try:
    data = request.json or {}
    anime = data.get('anime', 'ONE PIECE')
    temporada = int(data.get('temporada', 1))
    capitulo = int(data.get('capitulo', 1))
    idioma = data.get('idioma', 'Subtitulado')
    url_descarga = data.get('url_descarga')

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

    return jsonify({'status': 'success', 'id': nuevo_id}), 201
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 2. Entregar estrictamente UNA tarea pendiente a Google Colab
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
      return jsonify(dict(row))
    return jsonify(None)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 3. Marcar como completado cuando Colab termine (evita duplicados para siempre)
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
    return jsonify({'status': 'success'})
  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
