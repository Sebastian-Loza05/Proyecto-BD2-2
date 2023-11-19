from flask import request, jsonify
from app import app
import indiceInvertido as invert
import database


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

