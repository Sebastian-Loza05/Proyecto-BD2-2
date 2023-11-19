from rtree import index
import os
import ffmpeg
import librosa
import librosa.display
import pandas as pd

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


def create_index(mfccs_vector=None):
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
        # punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
        # punto = [float(x) for x in punto]
        # puntos.append(punto)
    indx = create_index(puntos)
    results = list(indx.nearest(coordinates=point, num_results=k))
    response = []
    for i in results:
        mf = mfcss_vectors[i]
        response.append({"track_name": mf["track_name"], "track_preview": mf["track_preview"]})
    indx.close()
    return response


# mfcss_vectors = {}
# puntos = []
# df = load_dataframes()
# for i, fila in df.iterrows():
#     mfcss_vectors[i] = fila
    # punto = fila["MFCC_Vector"].replace("[", "").replace("]", "").replace("\n", "").split(" ")
    # punto = [float(x) for x in punto]
    # puntos.append(punto)

# prueba = get_vector("cancion1.wav", True)
# knn_search(prueba, 15, mfcss_vectors)





