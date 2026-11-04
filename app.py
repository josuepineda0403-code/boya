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
      {'status': 'online', 'mensaje': '🚀 API Boya en Render Activa'}
  )


# Obtener solo UNA tarea pendiente para que Colab procese de a uno sin duplicar
@app.route('/api/siguiente-tarea', methods=['GET'])
def siguiente_tarea():
  try:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Trae exclusivamente la primera tarea que tenga estado pendiente
    cursor.execute(
        "SELECT * FROM cola_tareas WHERE estado = 'pendiente' LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row:
      return jsonify(dict(row))
    return jsonify(None)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Marcar tarea como completada y eliminarla de la cola activa para evitar duplicados
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  try:
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Opción A: Borrarla para que nunca se repita
    cursor.execute('DELETE FROM cola_tareas WHERE id = ?', (id_tarea,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Tarea completada y purgada'})
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# Agregar o actualizar tarea desde el panel web
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
          """
                UPDATE cola_tareas SET url_descarga = ?, estado = ? WHERE id = ?
            """,
          (url_descarga, estado, id_tarea),
      )
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'}), 200
  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)
