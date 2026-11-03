import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 👈 Esto habilita las peticiones cruzadas desde cualquier web (CORS)

DB_FILE = 'animes.db'


# Inicializar la base de datos SQLite local
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
            filecode TEXT,
            url_reproduccion TEXT,
            url_descarga_directa TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route('/')
def home():
  return jsonify({
      'status': 'online',
      'mensaje': '🚀 API Boya Autónoma con SQLite y CORS Activa',
  })


# 1. Tu Formulario Web envía la tarea aquí
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
      return jsonify({'error': 'La URL de descarga es obligatoria'}), 400

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

    return (
        jsonify({
            'status': 'success',
            'message': 'Tarea registrada en SQLite correctamente',
            'id': nuevo_id,
        }),
        201,
    )
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 2. Google Colab consulta los pendientes aquí
@app.route('/api/pendientes', methods=['GET'])
def obtener_pendientes():
  try:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tareas_animes WHERE estado = 'pendiente'")
    rows = cursor.fetchall()
    pendientes = [dict(row) for row in rows]
    conn.close()
    return jsonify(pendientes)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 3. Google Colab actualiza la tarea a completado aquí
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  try:
    data = request.json or {}
    filecode = data.get('filecode')
    url_reproduccion = data.get('url_reproduccion')
    url_descarga_directa = data.get('url_descarga_directa')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
            UPDATE tareas_animes 
            SET estado = 'completado', filecode = ?, url_reproduccion = ?, url_descarga_directa = ?
            WHERE id = ?
        """,
        (filecode, url_reproduccion, url_descarga_directa, id_tarea),
    )
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': f'Tarea {id_tarea} marcada como completada',
    })
  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
