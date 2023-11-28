import librosa
import librosa.display
import pandas as pd
import numpy as np

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
    mfcss_vectors = {}
    puntos = {}
    for i, fila in df.iterrows():
        track_id = i
        mfcss_vectors[track_id] = fila
        punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
        punto = [float(x) for x in punto]
        punto_info = {
            "track_id": fila["track_id"],
            "track_name": fila["track_name"],
            "track_artist": fila["track_artist"],
            "track_preview": fila["track_preview"],
            "lyrics": fila["lyrics"],
            "MFCC_Vector": punto,
            "duration": 30000,
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

def knn_searchS(query, C, k):
    distances = []

    for track_id, punto_info in C.items():
        vector = punto_info["MFCC_Vector"]
        distance = euclidean_distance(query, vector)
        distances.append((distance, track_id))
    distances.sort(key=lambda x: x[0])

    neighbors = distances[:int(k)]

    return neighbors

def range_search(query, C, radius):
    results = []

    for track_id, punto_info in C.items():
        vector = punto_info["MFCC_Vector"]
        distance = euclidean_distance(query, vector)

        if distance <= radius:
            results.append((distance, track_id))

    return results

