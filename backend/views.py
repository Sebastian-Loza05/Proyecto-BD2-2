from flask import request, jsonify, abort
from app import app
import indiceInvertido as invert
import database
import ffmpeg
import os
import json

import numpy as np

from indice_multidimensional.indice import (
    knn_search,
    faiss_search,
    get_vector,
    vectorize
)

@app.route('/faiss', methods=['POST'])
def search_faissa():
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
        vector = vectorize(output)
        # vector = get_vector(output)
        vector = np.array(vector)
        # print(vector[-1])
        # vector = np.trunc(vector * 10**7) / 10**7
        vector = vector.reshape(1, -1)

        # print(vector[-1][-1])
        print(vector)
        response = faiss_search(vector, top_k)

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
        # vector = get_vector(output)
        vector = vectorize(output)
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


