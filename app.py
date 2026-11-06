import os
import pymysql
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuración directa de tu MySQL en InfinityFree
DB_HOST = 'sql107.infinityfree.com'
DB_USER = 'if0_43337662'
DB_PASS = 'Siempresolo12'
DB_NAME = 'if0_43337662_gestor_animes'

def obtener_conexion():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return jsonify({
        'status': 'online',
        'mensaje': '🚀 API Central Render Activa (Directo a MySQL)',
    })

@app.route('/api/agregar', methods=['POST'])
def agregar_tarea():
    try:
        data = request.json or {}
        anime = data.get('anime', 'ONE PIECE')
        temporada = int(data.get('temporada', 1))
        capitulo = int(data.get('capitulo', 1))
        idioma = data.get('idioma', 'Latino')
        url_descarga = data.get('url_descarga')

        if not url_descarga:
            return jsonify({'error': 'La URL es obligatoria'}), 400

        connection = obtener_conexion()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO cola_tareas (anime, temporada, capitulo, idioma, url_descarga, estado) 
                VALUES (%s, %s, %s, %s, %s, 'pendiente')
            """
            cursor.execute(sql, (anime, temporada, capitulo, idioma, url_descarga))
            connection.commit()
            nuevo_id = cursor.lastrowid
        connection.close()

        print(f'📥 [NUEVA TAREA] ID: {nuevo_id} | {anime} T{temporada} C{capitulo}')
        return jsonify({'status': 'success', 'id': nuevo_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/siguiente', methods=['GET'])
def siguiente_tarea():
    try:
        connection = obtener_conexion()
        with connection.cursor() as cursor:
            # Selecciona la siguiente tarea pendiente
            cursor.execute("SELECT * FROM cola_tareas WHERE estado = 'pendiente' ORDER BY id ASC LIMIT 1")
            tarea = cursor.fetchone()
            
            if tarea:
                # Si el capítulo es mayor a 1, podemos buscar información del capítulo anterior
                # del mismo anime, temporada e idioma para rastrear su estructura o filecode base si se requiere
                anime_actual = tarea['anime']
                temp_actual = tarea['temporada']
                idioma_actual = tarea['idioma']
                cap_actual = tarea['capitulo']
                
                if cap_actual > 1:
                    cursor.execute("""
                        SELECT filecode, url_reproduccion FROM cola_tareas 
                        WHERE anime = %s AND temporada = %s AND idioma = %s AND capitulo = %s AND estado = 'completado'
                        LIMIT 1
                    """, (anime_actual, temp_actual, idioma_actual, cap_actual - 1))
                    cap_anterior = cursor.fetchone()
                    if cap_anterior:
                        # Inyectamos una referencia del capítulo anterior en la respuesta para que el worker la use de guía
                        tarea['referencia_anterior'] = cap_anterior['filecode']
                    else:
                        tarea['referencia_anterior'] = None

        connection.close()
        return jsonify(tarea if tarea else None)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/completار/<int:id_tarea>', methods=['POST']) # o /api/completar/<int:id_tarea>
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
    try:
        data = request.json or {}
        filecode = data.get('filecode', '')
        url_reproduccion = data.get('url_reproduccion', '')
        estado = data.get('estado', 'completado')

        # Actualización directa en MySQL solicitada por el usuario
        connection = obtener_conexion()
        with connection.cursor() as cursor:
            sql = """
                UPDATE cola_tareas 
                SET estado = %s, filecode = %s, url_reproduccion = %s 
                WHERE id = %s
            """
            cursor.execute(sql, (estado, filecode, url_reproduccion, id_tarea))
            connection.commit()
        connection.close()

        print(f'✅ [MySQL Actualizado] Tarea ID {id_tarea} -> Completado (Filecode: {filecode})')
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estado-global', methods=['GET'])
def estado_global():
    try:
        connection = obtener_conexion()
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM cola_tareas WHERE estado = 'pendiente'")
            resultado = cursor.fetchone()
            pendientes = resultado['total'] if resultado else 0
        connection.close()
        return jsonify({'status': 'success', 'pendientes': pendientes})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
