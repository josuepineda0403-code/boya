import os
from flask import Flask, jsonify, request
from supabase import Client, create_client

app = Flask(__name__)

# Credenciales seguras tomadas de las variables de entorno de Render
SUPABASE_URL = os.environ.get(
    'SUPABASE_URL', 'https://hghmometralnsgjqaawp.supabase.co'
)
SUPABASE_SECRET_KEY = os.environ.get(
    'SUPABASE_SECRET_KEY', 'sb_secret_3CWyezlbdueH0lQSyAa11A_oj41nC6T'
)

# Inicializar cliente oficial de Supabase en el servidor
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)


@app.route('/')
def home():
  return jsonify(
      {
          'status': 'online',
          'mensaje': '🚀 API Boya Maestra de Animes Activa y Segura',
      }
  )


# 1. Endpoint para que tu Formulario Web guarde tareas
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

    nueva_tarea = {
        'anime': anime,
        'temporada': temporada,
        'capitulo': capitulo,
        'idioma': idioma,
        'url_descarga': url_descarga,
        'estado': 'pendiente',
    }

    response = supabase.table('tareas_animes').insert(nueva_tarea).execute()

    return (
        jsonify(
            {
                'status': 'success',
                'message': 'Tarea registrada correctamente en la base de datos',
                'data': response.data,
            }
        ),
        201,
    )
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 2. Endpoint para que Google Colab consulte los capítulos pendientes
@app.route('/api/pendientes', methods=['GET'])
def obtener_pendientes():
  try:
    response = (
        supabase.table('tareas_animes')
        .select('*')
        .eq('estado', 'pendiente')
        .execute()
    )
    return jsonify(response.data)
  except Exception as e:
    return jsonify({'error': str(e)}), 500


# 3. Endpoint para que Google Colab marque el capítulo como completado
@app.route('/api/completar/<int:id_tarea>', methods=['POST'])
def completar_tarea(id_tarea):
  try:
    data = request.json or {}
    update_data = {
        'estado': 'completado',
        'filecode': data.get('filecode'),
        'url_reproduccion': data.get('url_reproduccion'),
        'url_descarga_directa': data.get('url_descarga_directa'),
    }

    response = (
        supabase.table('tareas_animes')
        .update(update_data)
        .eq('id', id_tarea)
        .execute()
    )

    return jsonify(
        {
            'status': 'success',
            'message': f'Tarea {id_tarea} marcada como completada',
            'data': response.data,
        }
    )
  except Exception as e:
    return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=10000)