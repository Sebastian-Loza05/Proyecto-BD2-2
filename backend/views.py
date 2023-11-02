from flask import request, jsonify
from app import app  
import indice


@app.route('/', methods=['GET'])
def hello():
    return "Hello from Flask"

@app.route('/invert_index', methods=['POST'])
def invert_index():
    
    query_text = request.json.get('query_text')
    top_k = int(request.json.get('top_k'))
    query_processed = indice.preprocess_text(query_text)
    results = indice.retrieve_top_k(query_processed, top_k, indice.merged_index, indice.num_docs)
    results_list = results.to_dict(orient='records')
    
    return jsonify(results_list)

@app.route('/psql', methods=['GET'])
def psql():
    return "Hello from psql"

@app.route('/mongo', methods=['GET'])
def mongo():
    return "Hello from mongo"