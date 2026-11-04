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
        CREATE TABLE IF NOT EXISTS cola_tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'episodio',
            anime TEXT,
            temporada INTEGER,
            capitulo INTEGER,
            idioma TEXT,
            url_descarga TEXT,
            estado TEXT DEFAULT 'faltante',
            filecode TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


@app.route('/')
def home():
  return jsonify(
      {'status': 'online', 'mensaje': '🚀 API Radar Inverso Activa'}
  )


# El Radar Inverso de Colab consulta este endpoint constantemente
@app.route('/api/siguiente-tarea', methods=['GET'])
def siguiente_tarea():
  try:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Busca estrictamente el primer registro con URL que esté pendiente
    cursor.execute(
        "SELECT * FROM cola_tareas WHERE estado = 'pendiente' AND url_descarga"
        " IS NOT NULL AND url_descarga != '' LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
      return jsonify(dict(row))
    return jsonify(None)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Al terminar el proceso, Colab marca la tarea como completada para evitar duplicados
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cola_tareas SET estado = 'completado' WHERE id = ?", (id_tarea,)
    )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Recibir la actualización manual desde tu panel PHP (guardar URL)
@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
  try:
    data = request.json or {}
    id_tarea = data.get('id_tarea')
    url_descarga = data.get('url_descarga', '')
    estado = 'pendiente' if url_descarga else 'faltante'

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if id_tarea:
      cursor.execute(
          "UPDATE cola_tareas SET url_descarga = ?, estado = ? WHERE id = ?",
          (url_descarga, estado, id_tarea),
      )
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})
  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
