import librosa
import librosa.display
import pandas as pd
import numpy as np

def load_dataframes():
    df = pd.read_csv("complete_spotify.csv", on_bad_lines="skip")
    mfcss_vectors = {}
    puntos = {}
    for i, fila in df.iterrows():
        track_id = i
        mfcss_vectors[track_id] = fila
        punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
        punto = [float(x) for x in punto]
        punto_info = {
            "track_name": fila["track_name"],
            "track_artist": fila["track_artist"],
            "lyrics": fila["lyrics"],
            "MFCC_Vector": punto
        }
        puntos[track_id] = punto_info
    return puntos

def get_mfcc_vector(file_path):
    audio_time_series, sampling_rate = librosa.load(file_path)
    mfcc_array = librosa.feature.mfcc(y=audio_time_series, sr=sampling_rate)
    mean_mfcc_array = np.mean(mfcc_array, axis=1)
    return mean_mfcc_array

def euclidean_distance(vector1, vector2):
    return np.linalg.norm(vector1 - vector2)

def knn_search(query, C, k):
    distances = []

    for track_id, punto_info in C.items():
        vector = punto_info["MFCC_Vector"]
        distance = euclidean_distance(query, vector)
        distances.append((distance, track_id))

    distances.sort(key=lambda x: x[0])

    neighbors = distances[:k]  

    return neighbors

def range_search(query, C, radius):
    results = []

    for track_id, punto_info in C.items():
        vector = punto_info["MFCC_Vector"]
        distance = euclidean_distance(query, vector)

        if distance <= radius:
            results.append((distance, track_id))

    return results

puntos = load_dataframes()
query = get_mfcc_vector("feel_alive.mp3")

k = 5

result = knn_search(query, puntos, k)
for distance, track_id in result:
    punto_info = puntos[track_id]
    track_name = punto_info["track_name"]
    print(f"track_id: {track_id}, track_name: {track_name}, Distancia: {distance}")


r = 32

range_result = range_search(query, puntos, r)
if range_result:
    print("Canciones similares dentro del rango:")
    for distance, track_id in range_result:
        punto_info = puntos[track_id]
        track_name = punto_info["track_name"]
        print(f"track_id: {track_id}, track_name: {track_name}, Distancia: {distance}")
else:
    print("No se encontraron canciones dentro del rango especificado.")