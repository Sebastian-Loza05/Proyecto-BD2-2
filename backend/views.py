from flask import request, jsonify, abort
from app import app
import indiceInvertido as invert
import database
import os
import json
import ffmpeg
import subprocess
import requests

import numpy as np

from indice_multidimensional.indice import (
    knn_search,
    faiss_search,
    get_vector,
    vectorize
)

from indice_multidimensional.Sec_Rango import (
    load_dataframes,
    get_mfcc_vector,
    knn_searchS,
    range_search
)

@app.route('/knn_search', methods=['POST'])
def sec_knn():
    error_422 = False
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
        puntos = load_dataframes()
        query = get_mfcc_vector(save_file)
        os.remove(save_file)

        print("faf")
        result = knn_searchS(query, puntos, top_k)
        print("faf")
        response = []
        for distance, track_id in result:
            punto_info = puntos[track_id]
            print("info: ", punto_info)
            response.append({
                "track_name": punto_info["track_name"],
                "track_preview": punto_info["track_preview"]
            })

        return jsonify({
            'success': True,
            'result': response
        })

    except Exception as e:
        print(e)
        if error_422:
            abort(422)
        else:
            abort(500)

@app.route('/range_search', methods=['POST'])
def sec_rango():
    error_422 = False
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
        puntos = load_dataframes()
        query = get_mfcc_vector(save_file)
        os.remove(save_file)

        result = range_search(query, puntos, top_k)
        response = []
        for distance, track_id in result:
            punto_info = puntos[track_id]
            response.append({
                "track_name": punto_info["track_name"],
                "track_preview": punto_info["track_preview"]
            })

        return jsonify({
            'success': True,
            'result': response
        })

    except Exception as e:
        print(e)
        if error_422:
            abort(422)
        else:
            abort(500)

@app.route('/faiss', methods=['POST'])
def search_faissa():
    print("faiss")
    error_422 = False
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
        vector = get_vector(save_file)
        os.remove(save_file)
        vector = np.array(vector)
        vector = vector.reshape(1, -1)
        response = faiss_search(vector, top_k)

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

    print("rtree")
    error_422 = False
    output = "uploads/output.wav"
    try:
        audio = request.files['audio']
        print(audio)
        if not audio:
            error_422 = True
            abort(422)

        data = request.form.get('json')
        json_data = json.loads(data)
        top_k = json_data['topK']
        print(top_k)

        save_file = f'uploads/{audio.filename}'
        print(save_file)
        audio.save(save_file)
        ffmpeg.input(save_file).output(output).run()
        vector = get_vector(save_file)
        # vector = vectorize(save_file)
        os.remove(save_file)
        vector = get_vector(output)
        # vector = vectorize(output)
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


@app.route('/spotify/token', methods=['POST'])
def get_spotify_token():
    code = request.json.get('code')
    redirect_uri = 'http://localhost:3000/spoti'
    client_id = '3d29c771b9a64a1d867e8fc98e855734'
    client_secret = '1949ef1c33a0420c91eac138b632ea59'

    auth_response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': client_id,
            'client_secret': client_secret
        },
    )

    if auth_response.status_code == 200:
        auth_response_data = auth_response.json()
        access_token = auth_response_data.get('access_token')
        refresh_token = auth_response_data.get('refresh_token')
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token
        })
    else:
        return jsonify({'message': 'Invalid code'}), 400


@app.route('/spotify/track/<track_id>', methods=['GET'])
def get_track_details(track_id):
    access_token = request.headers.get('Authorization').split(" ")[1]
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    track_response = requests.get(
        f'https://api.spotify.com/v1/tracks/{track_id}',
        headers=headers
    )

    if track_response.status_code == 200:
        track_data = track_response.json()
        image_url = track_data['album']['images'][0]['url']  # Obtén la URL de la imagen más grande
        preview_url = track_data.get('preview_url', None)
        return jsonify({
            'image_url': image_url,
            'name': track_data['name'],
            'artists': [artist['name'] for artist in track_data['artists']],
            'preview_url': preview_url
        })
    else:
        print(f"Error fetching track details: {track_response.status_code}")
        print(f"Response: {track_response.json()}")
        return jsonify({'message': 'Could not fetch track details'}), 400


@app.route('/spotify/playlist/<playlist_id>', methods=['GET'])
def get_playlist_tracks(playlist_id):
    access_token = request.headers.get('Authorization').split(" ")[1]
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Obtener las 50 primeras canciones de la playlist
    playlist_response = requests.get(
        f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50',
        headers=headers
    )

    if playlist_response.status_code == 200:
        playlist_data = playlist_response.json()
        tracks = []
        for item in playlist_data['items']:
            track = item['track']
            track_info = {
                'name': track['name'],
                'artists': [artist['name'] for artist in track['artists']],
                'duration_ms': track['duration_ms'],
                'preview_url': track['preview_url'],
                'album': {
                    'name': track['album']['name'],
                    'images': track['album']['images']
                }
            }
            tracks.append(track_info)

        return jsonify(tracks)
    else:
        print(f"Error fetching playlist details: {playlist_response.status_code}")
        print(f"Response: {playlist_response.json()}")
        return jsonify({'message': 'Could not fetch playlist details'}), 400
