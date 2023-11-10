import math
import pickle
import os
from collections import defaultdict
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pandas as pd
from itertools import islice
from collections import Counter
import json

nltk.download('stopwords')

stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')

CANTIDAD_INDICES = 18
CANTIDAD_DOCS = 18454
# CANTIDAD_DOCS = 28
NORMA = []
RAM = 100000
MAX_POSTINGS_LENGHT = 40
CARPETA = True
DF = pd.read_csv('spotify.csv', on_bad_lines='skip')

def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

def score_idf(N, df_t):
    return math.log10(N / (1 + df_t))  # Suavización añadida al IDF

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    tokens = [valor.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u") for valor in tokens]

    stemmer = stemmer_spanish if "el" in tokens or "la" in tokens else stemmer_english
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def load_full_dataframe():
    df = pd.read_csv('spotify.csv', on_bad_lines='skip')
    df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
    df['processed_text'] = df['combined_text'].apply(preprocess_text)
    return df

def borrar_archivos_previos():
    for elemento in os.listdir("indicesF1"):
        elemento_r = os.path.join("indicesF1", elemento)
        os.remove(elemento_r)

    for elemento in os.listdir("indicesF2"):
        elemento_r = os.path.join("indicesF2", elemento)
        os.remove(elemento_r)

    for elemento in os.listdir("blocks"):
        elemento_r = os.path.join("blocks", elemento)
        os.remove(elemento_r)

    for elemento in os.listdir("indices"):
        elemento_r = os.path.join("indices", elemento)
        os.remove(elemento_r)

def print_indice(long=0):
    carp = "F2" if CARPETA else "F1"
    if long == 0:
        long = CANTIDAD_INDICES
    for i in range(long):
        with open(f"indices{carp}/indice_invertido{i}.pkl", 'rb') as file:
            indice = pickle.load(file)
            indice_bonito = json.dumps(indice, indent=4)
        print(indice_bonito)

def write_to_disk(inv_index, postings, indice, last_block_num):
    sorted_index = dict(sorted(inv_index.items()))
    with open(f"indices/indice_invertido{indice}.pkl", "wb") as file:
        pickle.dump(sorted_index, file)

    for i in range(len(postings)):
        # print(f"bloque{i+last_block_num}: ", postings[i])
        with open(f"blocks/bloque{i+last_block_num}.pkl", "wb") as file:
            pickle.dump(postings[i], file)

def generate_tfw(docs):
    borrar_archivos_previos()
    print("Eliminó todo")
    inv_index = {}
    posting_lists = []
    block_num = 0
    last_block_num = 0
    indice = 0
    bloque_simulado = {f'clave{i}': f'valor{i}' for i in range(MAX_POSTINGS_LENGHT)}
    i = 0
    for doc_id, doc in enumerate(docs):
        print(f"doc{doc_id}")
        terms = doc.split(' ')
        terms_counted = Counter(terms)

        for term, freq in terms_counted.items():
            print(i, ": ", term)
            if term not in inv_index:
                tam1 = len(pickle.dumps({**inv_index, term: [1, block_num]}))
                tam2 = len(pickle.dumps(bloque_simulado))
                tamaño = tam1 + tam2
                if tamaño > RAM:
                    write_to_disk(inv_index, posting_lists, indice, last_block_num)
                    indice += 1
                    last_block_num = block_num
                    inv_index.clear()
                    posting_lists.clear()
                inv_index[term] = [1, block_num]  # [df, block_num]
                block_num += 1
                posting_lists.append({'next': -1, doc_id: score_tf(freq)})
            else:
                posting_lists[inv_index[term][1] - last_block_num][doc_id] = score_tf(freq)
                inv_index[term][0] += 1
            i += 1
    global CANTIDAD_INDICES
    CANTIDAD_INDICES = indice
    print(block_num)
    return block_num

def combine_blocks(bloque1, bloque2, llave_bloque1, llave_bloque2):
    bloque_escribir = {**bloque2}
    next = -1
    llave_bloque = llave_bloque2
    while bloque1["next"] != -1:
        next = bloque1["next"]
        bloque1.pop("next")
        for key, value in bloque1.items():
            if len({**bloque_escribir, key: value}) > MAX_POSTINGS_LENGHT:
                bloque_escribir["next"] = llave_bloque1
                # print(bloque_escribir)
                with open(f"blocks/bloque{llave_bloque}.pkl", "wb") as output:
                    pickle.dump(bloque_escribir, output)
                llave_bloque = llave_bloque1
                llave_bloque1 = next
                bloque_escribir.clear()
                bloque_escribir["next"] = -1
                bloque_escribir[key] = value
            else:
                bloque_escribir[key] = value

        with open(f"blocks/bloque{next}.pkl", 'rb') as file:
            bloque1 = pickle.load(file)

    bloque1.pop("next")
    for key, value in bloque1.items():
        if len({**bloque_escribir, key: value}) > MAX_POSTINGS_LENGHT:
            bloque_escribir["next"] = llave_bloque1
            # print(bloque_escribir)
            with open(f"blocks/bloque{llave_bloque}.pkl", "wb") as output:
                pickle.dump(bloque_escribir, output)
            llave_bloque = llave_bloque1
            bloque_escribir.clear()
            bloque_escribir["next"] = -1
            bloque_escribir[key] = value
        else:
            bloque_escribir[key] = value

    # print(bloque_escribir)
    with open(f"blocks/bloque{llave_bloque}.pkl", "wb") as output:
        pickle.dump(bloque_escribir, output)


def combine_indices(indice_mergeado, key, value_k1, value_k2):
    indice_mergeado[key] = [
        value_k1[0] + value_k2[0],
        value_k2[1]
    ]
    llave_bloque = value_k2[1]

    with open(f"blocks/bloque{value_k1[1]}.pkl", 'rb') as file:
        bloque1 = pickle.load(file)

    with open(f"blocks/bloque{value_k2[1]}.pkl", 'rb') as file:
        bloque2 = pickle.load(file)
    while bloque2["next"] != -1:
        llave_bloque = bloque2["next"]
        with open(f"blocks/bloque{bloque2['next']}.pkl", 'rb') as file:
            bloque2 = pickle.load(file)

    bloque = {**bloque2, **bloque1}
    # print("Bloques----------------------------------------------------------")
    # print(f"{value_k1[1]}: ", bloque1)
    # print(f"{llave_bloque}: ", bloque2)
    # print(bloque)
    if len(bloque) > MAX_POSTINGS_LENGHT:
        # print("Excede")
        combine_blocks(bloque1, bloque2, value_k1[1], llave_bloque)
    else:
        with open(f"blocks/bloque{llave_bloque}.pkl", 'wb') as file:
            pickle.dump(bloque, file)
        # print(f"Elimando bloque{value_k1[1]}")
        os.remove(f"blocks/bloque{value_k1[1]}.pkl")

def merge_interno(indice_local, idx_actual, cantidad):
    global CARPETA
    previo = "F1"
    nuevo = "F2"
    if CARPETA:
        previo = "F2"
        nuevo = "F1"
    CARPETA = not CARPETA

    indice_mergeado = {}
    i = 0
    indice_archivo = -1
    bloque_simulado = {f'clave{j}': f'valor{j}' for j in range(MAX_POSTINGS_LENGHT)}
    # print("local: ", indice_local)
    while i < cantidad and i < idx_actual:
        with open(f"indices{previo}/indice_invertido{i}.pkl", "rb") as file:
            indice_disco = pickle.load(file)
        os.remove(f"indices{previo}/indice_invertido{i}.pkl")
        # print("disco: ", indice_disco)
        while len(indice_disco) != 0 and len(indice_local) != 0:
            key1 = next(iter(indice_local))
            key2 = next(iter(indice_disco))
            tam1 = len(pickle.dumps({**indice_mergeado, **{key1: indice_local[key1]}}))
            tam2 = len(pickle.dumps(bloque_simulado))
            if tam1 + tam2 > RAM:
                indice_archivo += 1
                with open(f"indices{nuevo}/indice_invertido{indice_archivo}.pkl", 'wb') as file:
                    pickle.dump(indice_mergeado, file)
                indice_mergeado.clear()

            if key1 == key2:
                indice_mergeado[key1] = [0, 0]
                combine_indices(indice_mergeado, key1, indice_local[key1], indice_disco[key2])
                indice_disco.pop(key2)
                indice_local.pop(key1)
            elif key1 < key2:
                indice_mergeado[key1] = indice_local[key1]
                indice_local.pop(key1)
            else:
                indice_mergeado[key2] = indice_disco[key2]
                indice_disco.pop(key2)

        while len(indice_disco) != 0:
            key = next(iter(indice_disco))
            tam1 = len(pickle.dumps({**indice_mergeado, **{key: indice_disco[key]}}))
            tam2 = len(pickle.dumps(bloque_simulado))
            if tam1 + tam2 > RAM:
                indice_archivo += 1
                with open(f"indices{nuevo}/indice_invertido{indice_archivo}.pkl", 'wb') as file:
                    pickle.dump(indice_mergeado, file)
                indice_mergeado.clear()
            else:
                indice_mergeado[key] = indice_disco[key]
                indice_disco.pop(key)
        i += 1
    indice_mergeado = {**indice_mergeado, **indice_local}
    if len(indice_mergeado) != 0:
        indice_archivo += 1
        with open(f"indices{nuevo}/indice_invertido{indice_archivo}.pkl", 'wb') as file:
            pickle.dump(indice_mergeado, file)

    # print_indice(indice_archivo + 1)
    # input()
    return indice_archivo + 1

def actualizar_block(bloque, idf, norma):
    with open(f"blocks/bloque{bloque}.pkl", "rb") as file:
        data = pickle.load(file)

    for key in data.keys():
        if key != 'next':
            data[key] = data[key] * idf
            norma[key] += data[key] ** 2

    if data['next'] != -1:
        actualizar_block(data['next'], idf, norma)
    # print(data)

    with open(f"blocks/bloque{bloque}.pkl", 'wb') as file:
        pickle.dump(data, file)

def actualizar_tf_idf(norma):
    indice_archivos = 0
    carp = "F2" if CARPETA else "F1"
    while os.path.exists(f"indices{carp}/indice_invertido{indice_archivos}.pkl"):
        with open(f"indices{carp}/indice_invertido{indice_archivos}.pkl", "rb") as file:
            dic_indic_disk = pickle.load(file)

        for key, valor in dic_indic_disk.items():
            idf = score_idf(CANTIDAD_DOCS, valor[0])
            dic_indic_disk[key][0] = idf
            actualizar_block(dic_indic_disk[key][1], idf, norma)

        with open(f"indices{carp}/indice_invertido{indice_archivos}.pkl", 'wb') as file:
            pickle.dump(dic_indic_disk, file)

        indice_archivos += 1


def merge(cantidad_bloques):
    global CANTIDAD_INDICES
    idx_actual = 0
    cantidad = 0
    print(CANTIDAD_INDICES)
    while idx_actual != CANTIDAD_INDICES:
        print(idx_actual)
        with open(f"indices/indice_invertido{idx_actual}.pkl", "rb") as file:
            indice_local = pickle.load(file)
        # print(indice_local)
        cantidad = merge_interno(indice_local, idx_actual, cantidad)
        print(cantidad, idx_actual + 1)
        os.remove(f"indices/indice_invertido{idx_actual}.pkl")
        idx_actual += 1
        # print(indice_local)
    global NORMA
    CANTIDAD_INDICES = cantidad
    norma = [0] * CANTIDAD_DOCS
    actualizar_tf_idf(norma)
    norma = [math.sqrt(norma[i]) for i in range(CANTIDAD_DOCS)]
    NORMA = norma
    with open("norma.pkl", "wb") as file:
        pickle.dump(NORMA, file)
    NORMA.clear()
    norma.clear()
    # print_indice()
    print(norma)

def wtf_query(textQuery):
    tokens = preprocess_text(textQuery)
    query_frecuency = {}
    for i in tokens.split(' '):
        if i not in query_frecuency:
            query_frecuency[i] = 1
        else:
            query_frecuency[i] += 1
    for term, tf in query_frecuency.items():
        query_frecuency[term] = score_tf(tf)

    return query_frecuency

def binary_recollection(word):
    # indiceinvertido 0 -> 1
    # bloque 0 -> 1
    carp = "F2" if CARPETA else "F1"
    left = 0
    right = CANTIDAD_INDICES - 1
    while left <= right:
        half = (left + right) // 2
        with open(f'indices{carp}/indice_invertido' + str(half) + '.pkl', 'rb') as mini_dic:
            dic_keys = pickle.load(mini_dic)

        if word in dic_keys:
            # print(dic_keys)
            return dic_keys[word]
        elif next(iter(dic_keys)) < word:
            left = half + 1
        else:
            right = half - 1

    return -1, -1

def documentos_topK(query, topk):
    query_frecuency = wtf_query(query)
    global NORMA
    with open("norma.pkl", "rb") as file:
        NORMA = pickle.load(file)
    norm_query = 0
    for i in query_frecuency.keys():
        idf_palabra_bloque = binary_recollection(i)
        query_frecuency[i] = [query_frecuency[i] * idf_palabra_bloque[0], idf_palabra_bloque[1]]
    # print("query:", query_frecuency)

    docs = {}
    for key in query_frecuency.keys():
        norm_query += (query_frecuency[key][0]**2)
        next = query_frecuency[key][1]
        while next != -1:
            with open(f"blocks/bloque{next}.pkl", 'rb') as file:
                data_blocks = pickle.load(file)

            for key_ in data_blocks.keys():
                if key_ != 'next':
                    if data_blocks[key_] in docs:
                        docs[key_] += query_frecuency[key][0] * data_blocks[key_]
                    else:
                        docs[key_] = query_frecuency[key][0] * data_blocks[key_]

            next = data_blocks['next']

    for key in docs.keys():
        docs[key] = (math.sqrt(docs[key])) / (math.sqrt(norm_query) * math.sqrt(NORMA[key]))

    print("---", docs)
    resultado = dict(sorted(docs.items(), key=lambda item: item[1], reverse=True))

    contador = 0
    topkDocuments = []
    for i in resultado.keys():
        topkDocuments.append(i)
        contador += 1
        if contador == topk:
            break

    return topkDocuments

def get_spotify_docs(query, topk):
    docs = documentos_topK(query, topk)
    results = []
    for i in docs:
        new = {}
        new["nombre"] = DF.at[i, "track_name"]
        new["artista"] = DF.at[i, "track_artist"]
        new["letra"] = DF.at[i, "lyrics"]
        results.append(new)
    return results


# Main
# canciones = load_full_dataframe()
# docs = canciones['processed_text'].tolist()
# cantidad_bloques = generate_tfw(docs)
# merge(cantidad_bloques)
# print(documentos_topK("I'm trying to reach goals", 10))
