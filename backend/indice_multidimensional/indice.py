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
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)
    res = []
    for coef in mfccs:
        rango = len(coef) // 2
        inicio = 0
        for i in range(2):
            if (len(coef[inicio + rango:]) < rango):
                li = coef[inicio:]
                res.append(sum(li) / len(li))
                break
            li = coef[inicio:inicio + rango]
            res.append(sum(li) / len(li))
            inicio += rango
    if (len(res) != 40):
        print("ERROR: ", filename)
        exit(0)
    return res

def create_indexRtree(mfccs_vector):
    prop = index.Property()
    prop.dimension = 40
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
    df = load_dataframesF()
    puntos = []
    for i, fila in df.iterrows():
        mfcss_vectors[i] = fila
        # punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")

        punto = fila["vectores_100"].replace("[", "").replace("]", "").replace("\n", "").split(",")
        if len(punto) == 40:
            punto = [float(x) for x in punto]
            puntos.append(punto)

    indx = create_indexRtree(puntos)
    print("amen")
    results = list(indx.nearest(coordinates=point, num_results=k))
    print("amen")
    print(results)
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
    dimension = 100
    index = faiss.IndexHNSWFlat(40, 16)
    # index.hnsw.efConstruction = 40
    puntos = []
    for value in mfcss_vectors.values():
        # point = value["MFCC_Vector"].replace(
        point = value["vectores_100"].replace(
            "[", "").replace(
            "]", "").replace(
            "\n", "").split(",")
        if len(point) == 40:
            point = [float(x) for x in point[:dimension]]
            puntos.append(point)
    puntos = np.array(puntos)
    # puntos = np.trunc(puntos * 10**7) / 10**7
    # pca = PCA(n_components=20)
    # puntos_nuevos = pca.fit_transform(puntos)
    # puntos_nuevos = np.array(puntos_nuevos, dtype='float32')
    # index.add(puntos_nuevos)
    # index.add(puntos)
    #
    index.add(puntos)
    # tamaño_lote = 1000  # Ajusta esto según tu entorno y recursos disponibles
    # num_puntos = puntos.shape[0]
    # try:
    #     for i in range(0, num_puntos, tamaño_lote):
    #         lote = puntos[i:i + tamaño_lote]
    #         index.add(lote)
    #         print(f"Lote {i // tamaño_lote} añadido al índice")
    # except Exception as e:
    #     print("Error ocurrido:", e)
    #     traceback.print_exc()
    # # faiss.write_index(index, 'puntosFaiss.index')
    # print("asd")
    return index

    # dimension = 100
    # quantizer = faiss.IndexFlatL2(dimension)
    # nlist = 100  # Número de listas invertidas (clústeres)
    # index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)
    # puntos = []
    # for value in mfcss_vectors.values():
    #     point = value["vectores_600"].replace(
    #         "[", "").replace(
    #         "]", "").replace(
    #         "\n", "").split(",")
    #     if len(point) == 600:
    #         point = [float(x) for x in point[:dimension]]
    #         puntos.append(point)
    #
    # puntos = np.array(puntos)
    # num_data_points = 10000
    # data = np.random.random((num_data_points, dimension)).astype('float32')
    # assert not index.is_trained
    # index.train(data)  # Entrenamiento con un subconjunto de los datos
    # assert index.is_trained
    # # index.add(puntos)
    # # faiss.write_index(index, 'puntosFaiss.index')
    # return index

def faiss_search(vec, topk):
    df = load_dataframesF()
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
            "track_name": mf["track_name"],
            "track_preview": mf["track_preview"]
        })

    return response

