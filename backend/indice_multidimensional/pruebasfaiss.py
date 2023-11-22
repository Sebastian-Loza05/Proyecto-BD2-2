import faiss
import ffmpeg
import numpy as np
import time
import pandas as pd
import librosa

def load_dataframes():
    df = pd.read_csv("complete_spotify.csv", on_bad_lines="skip")
    return df

def convert_to_wav(filename):
    nombre = filename.split(".")[0]
    ffmpeg.input("mp3s/" + filename).output("wavs/" + nombre + ".wav").run()

def get_vector(filename):
    x, sr = librosa.load(filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)
    res = []
    for coef in mfccs:
        suma = sum(coef)
        res.append(suma / len(coef))
    return res

dimension = 20

num_vectors = 10000

df = load_dataframes()
mfcss_vectors = {}
for i, fila in df.iterrows():
    mfcss_vectors[i] = fila

puntos = []
for value in mfcss_vectors.values():
    point = value["MFCC_Vector"].replace(
        "[", "").replace(
        "]", "").replace(
        "\n", "").split(" ")
    point = [float(x) for x in point]
    puntos.append(point)

puntos = np.array(puntos)

k = 5

vector = get_vector("pruebas/feel_alive.wav")
vector = np.array(vector)
vector = vector.reshape(1, -1)

num_queries = 100
queries = np.random.rand(num_queries, dimension).astype('float32')

for m in [4, 8, 16, 32, 64]:
    print(f"Probando m={m}")

    index = faiss.IndexHNSWFlat(dimension, m)
    start_time = time.time()
    index.add(puntos)
    construction_time = time.time() - start_time
    print(f"Tiempo de construcción del índice: {construction_time:.5f} segundos")

    start_time = time.time()
    D, I = index.search(vector, k)
    search_time = time.time() - start_time
    print(f"Tiempo de búsqueda: {search_time:.10f} segundos")
    print()

