from rtree import index
import os
import ffmpeg
from pathlib import Path
import librosa
import librosa.display
import pandas as pd

def load_dataframes():
    df = pd.read_csv("../../VectoresCaracteristicos/complete_spotify.csv", on_bad_lines="skip")
    print(df.at[0, "MFCC_Vector"])
    return df

def convert_to_wav(filename):
    nombre = filename.split(".")[0]
    ffmpeg.input("mp3s/" + filename).output("wavs/" + nombre + ".wav").run()

def get_vector(filename, prueba):
    if prueba:
        x, sr = librosa.load("pruebas/" + filename)
    else:
        x, sr = librosa.load("wavs/" + filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=13)
    res = []
    for coef in mfccs:
        suma = sum(coef)
        res.append(suma / len(coef))
    return res


def create_index(mfccs_vector):
    if os.path.exists("puntos.data"):
        os.remove("puntos.data")
    if os.path.exists("puntos.index"):
        os.remove("puntos.index")

    prop = index.Property()
    prop.dimension = 20
    prop.buffering_capacity = 2 * 20
    prop.dat_extension = 'data'
    prop.idx_extension = 'index'
    indx = index.Index('puntos', properties=prop)
    for i, p in enumerate(mfccs_vector):
        indx.insert(i, p)
    return indx

def knn_search(indx, point, k, mfcss_vectors):
    results = list(indx.nearest(coordinates=point, num_results=k))
    print(list(mfcss_vectors.keys())[results[0]])
    print(results)


mfcss_vectors = {}
puntos = []
df = load_dataframes()
for i, fila in df.iterrows():
    mfcss_vectors[i] = fila
    punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
    punto = [float(x) for x in punto]
    puntos.append(punto)

indx = create_index(puntos)
# prueba = get_vector("Voz_003.wav", True)
# knn_search(indx, prueba, 2, mfcss_vectors)




