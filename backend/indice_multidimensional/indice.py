import os
from rtree import index
import faiss
import numpy as np
from sklearn.decomposition import PCA
import traceback
import pandas as pd
import ffmpeg
import librosa

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
    return df

def load_dataframesF():
    df = pd.read_csv("indice_multidimensional/spotify_final.csv", on_bad_lines="skip")
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

def vectorize(filename):
    x, sr = librosa.load(filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20, hop_length=742000)
    res = []
    # 2.- PCA
    for coef in mfccs:
        for dato in coef:
            res.append(dato)
    print(len(res))
    if (len(res) != 20):
        print("ERROR: ", filename)
        exit(0)
    return res

def create_indexRtree(mfccs_vector):
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
    print(len(mfccs_vector))
    for i, p in enumerate(mfccs_vector):
        indx.insert(i, p)
    return indx

def knn_search(point, k):
    mfcss_vectors = {}
    df = load_dataframes()
    puntos = []
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
        punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")

        if len(punto) == 20:
            punto = [float(x) for x in punto]
            puntos.append(punto)
    indx = create_indexRtree(puntos)
    results = list(indx.nearest(coordinates=point, num_results=int(k)))
    response = []
    for i in results:
        mf = mfcss_vectors[i]
        response.append({
            "track_id": mf["track_id"],
            "track_name": mf["track_name"],
            "track_artist": mf["track_artist"],
            "lyrics": mf["lyrics"],
            "track_preview": mf["track_preview"],
            "duration": 30000
        })
    indx.close()
    print(response)
    return response

def create_indexFaiss(mfcss_vectors=None):
    if os.path.exists("puntosFaiss.index"):
        index = faiss.read_index("puntosFaiss.index")
        return index
    dimension = 20
    index = faiss.IndexHNSWFlat(20, 16)
    puntos = []
    for value in mfcss_vectors.values():
        point = value["MFCC_Vector"].replace(
            "[", "").replace(
            "]", "").replace(
            "\n", "").split(" ")
        if len(point) == 20:
            point = [float(x) for x in point[:dimension]]
            puntos.append(point)
    puntos = np.array(puntos)
    try:
        index.add(puntos)
    except Exception as e:
        print("Error ocurrido:", e)
        traceback.print_exc()
    faiss.write_index(index, 'puntosFaiss.index')
    return index

def faiss_search(vec, topk):
    df = load_dataframes()
    mfcss_vectors = {}
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
    indx = create_indexFaiss(mfcss_vectors)
    response = []
    print("Asd")
    try:
        print("a")
        # indx.hnsw.efSearch = 100  # o un valor más alto para una mayor precisión
        distancias, indices = indx.search(vec, topk)
    except Exception as e:
        print("Error ocurrido:", e)
        traceback.print_exc()
    for i in indices[0]:
        mf = mfcss_vectors[i]
        response.append({
            "track_id": mf["track_id"],
            "track_name": mf["track_name"],
            "track_artist": mf["track_artist"],
            "lyrics": mf["lyrics"],
            "track_preview": mf["track_preview"],
            "duration": 30000
        })

    return response

