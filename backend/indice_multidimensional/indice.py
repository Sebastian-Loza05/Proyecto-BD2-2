import os
from rtree import index
import faiss
import numpy as np

import pandas as pd
import ffmpeg
import librosa

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
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

def create_indexRtree(mfccs_vector=None):
    prop = index.Property()
    prop.dimension = 20
    prop.buffering_capacity = 2 * 20
    prop.storage = index.RT_Disk
    prop.overwrite = False
    if os.path.exists("puntos.dat") and os.path.exists("puntos.idx"):
        idx = index.Rtree('puntos', properties=prop)
        return idx
    prop.dat_extension = 'dat'
    prop.idx_extension = 'idx'
    indx = index.Index('puntos', properties=prop)
    for i, p in enumerate(mfccs_vector):
        indx.insert(i, p)
    return indx

def knn_search(point, k):
    mfcss_vectors = {}
    df = load_dataframes()
    puntos = []
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
    indx = create_indexRtree(puntos)
    results = list(indx.nearest(coordinates=point, num_results=k))
    response = []
    for i in results:
        mf = mfcss_vectors[i]
        response.append({
            "track_name": mf["track_name"],
            "track_preview": mf["track_preview"]
        })
    indx.close()
    return response

def create_indexFaiss(mfcss_vectors=None):
    if os.path.exists("puntosFaiss.index"):
        index = faiss.read_index("puntosFaiss.index")
        return index
    index = faiss.IndexFlatL2(20)
    puntos = []
    for value in mfcss_vectors.values():
        point = value["MFCC_Vector"].replace(
            "[", "").replace(
            "]", "").replace(
            "\n", "").split(" ")
        point = [float(x) for x in point]
        puntos.append(point)

    puntos = np.array(puntos)
    index.add(puntos)
    faiss.write_index(index, 'puntosFaiss.index')
    return index

def faiss_search(vec, topk):
    df = load_dataframes()
    mfcss_vectors = {}
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
    indx = create_indexFaiss(mfcss_vectors)
    response = []
    distancias, indices = indx.search(vec, topk)
    for i in indices[0]:
        mf = mfcss_vectors[i]
        response.append({
            "track_name": mf["track_name"],
            "track_preview": mf["track_preview"]
        })

    return response

