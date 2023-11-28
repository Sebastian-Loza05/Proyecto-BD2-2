import os
import pandas as pd
import librosa

# 30
path = 'musicas/'

def load_dataframes():
    df = pd.read_csv("indice_multidimensional/complete_spotify.csv", on_bad_lines="skip")
    df["vectores_100"] = " "
    return df

def vectorize(filename):
    x, sr = librosa.load(filename)
    mfccs = librosa.feature.mfcc(y=x, sr=sr, n_mfcc=20)
    res = []
    for coef in mfccs:
        rango = len(coef) // 5
        inicio = 0
        for i in range(5):
            if (len(coef[inicio + rango:]) < rango):
                li = coef[inicio:]
                res.append(sum(li) / len(li))
                break
            li = coef[inicio:inicio + rango]
            res.append(sum(li) / len(li))
            inicio += rango
    if (len(res) != 100):
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
        break
    df.to_csv("indice_multidimensional/spotify_final.csv", index=False)


main()

