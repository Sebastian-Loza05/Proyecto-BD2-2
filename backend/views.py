from flask import request, jsonify, abort
from app import app
import indiceInvertido as invert
import database
import ffmpeg
import os
from indice_multidimensional.rtree_method import knn_search, get_vector
import json


@app.route('/', methods=['GET'])
def hello():
    return "Hello from Flask"

@app.route('/invert_index', methods=['POST'])
def invert_index():
    query_text = request.json.get('textQuery')
    top_k = int(request.json.get('topK'))
    results = invert.get_spotify_docs(query_text, top_k)
    print(results)
    return jsonify(results)

@app.route('/psql', methods=['POST'])
def psql():
    data = request.get_json()
    query = data["textQuery"]
    top_k = int(data["topK"])

    conn = database.connect()
    results = database.search(conn, query, top_k)
    conn.close()
    print("Llamado a PSQL")
    return jsonify(results)

@app.route('/mongo', methods=['GET'])
def mongo():
    return "Hello from mongo"

@app.route('/rtree', methods=['POST'])
def search_rtree():
    error_422 = False
    output = "uploads/output.wav"
    try:
        audio = request.files['audio']

        if not audio:
            error_422 = True
            abort(422)

        data = request.form.get('json')
        json_data = json.loads(data)
        top_k = json_data['topK']

        save_file = f'uploads/{audio.filename}'
        audio.save(save_file)
        ffmpeg.input(save_file).output(output).run()
        os.remove(save_file)
        vector = get_vector(output)
        response = knn_search(vector, top_k)
        os.remove(output)
        return jsonify({
            'success': True,
            'results': response
        })

    except Exception as e:
        print(e)
        if error_422:
            abort(422)
        else:
            abort(500)

