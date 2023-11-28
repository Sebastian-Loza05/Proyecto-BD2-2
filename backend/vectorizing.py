import os
import pandas as pd
import librosa

# 30
path = 'actual_music/'

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
    df["vectores_100"] = " "
    return df

def vectorize(filename):
    x, sr = librosa.load(filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20, hop_length=512)
    # mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20, hop_length=742000)
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

def main():
    df = load_dataframes()
    for nombre in os.listdir(path):
        filedirection = path + nombre
        vector = vectorize(filedirection)
        str_vector = str(vector)
        print(filedirection)
        df.loc[df["mp3 File"] == filedirection.replace("/", "\\"), "vectores_100"] = str_vector
    df.to_csv("indice_multidimensional/spotify_final.csv", index=False)


main()

