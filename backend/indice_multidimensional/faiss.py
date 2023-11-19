import faiss
import ffmpeg
import librosa
import librosa.display
import pandas as pd
import numpy as np

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
    return df

def convert_to_wav(filename):
    nombre = filename.split(".")[0]
    ffmpeg.input("mp3s/" + filename).output("wavs/" + nombre + ".wav").run()

def get_vector(filename, prueba):
    if prueba:
        x, sr = librosa.load("pruebas/" + filename)
    else:
        x, sr = librosa.load("wavs/" + filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)
    res = []
    for coef in mfccs:
        suma = sum(coef)
        res.append(suma / len(coef))
    return res

def create_indexf(dimension):
    mfcss_vectors = {}
    df = load_dataframes()
    puntos = []
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
        punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
        punto = [float(x) for x in punto]
        puntos.append(punto)

    index = faiss.IndexFlatL2(dimension)
    puntos = np.array(puntos)
    index.add(puntos)

    return index, mfcss_vectors

def search_faiss(topk, index, data, vec):
    distancias, indices = index.search(vec, topk)
    response = []
    for i in indices[0]:
        mf = data[i]
        response.append({"track_name": mf["track_name"], "track_preview": mf["track_preview"]})

    return response

