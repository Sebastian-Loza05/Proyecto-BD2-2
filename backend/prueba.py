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

page_size = 200
lista_tam = 100
stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')


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
    df = pd.read_csv('canciones.csv', on_bad_lines='skip')
    df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
    df['processed_text'] = df['combined_text'].apply(preprocess_text)
    return df

def write_to_disk(inv_index, postings, indice, last_block_num):
    sorted_index = dict(sorted(inv_index.items()))
    with open(f"indices/indice_invertido{indice}.pkl", "wb") as file:
        pickle.dump(sorted_index, file)

    for i in range(len(postings)):
        with open(f"blocks/bloque{i+last_block_num}.pkl", "wb") as file:
            pickle.dump(postings[i], file)

def generate_tfw(docs):
    inv_index = {}
    posting_lists = []
    block_num = 0
    last_block_num = 0
    indice = 0

    for doc_id, doc in enumerate(docs):
        terms = doc.split(' ')
        terms_counted = Counter(terms)
        # print(doc_id, ": ", Counter(terms))

        for term, freq in terms_counted.items():
            tamaño = len(pickle.dumps(inv_index)) + len(pickle.dumps(posting_lists))
            # print(inv_index, posting_lists)
            # print(tamaño, page_size)
            if tamaño > page_size:
                write_to_disk(inv_index, posting_lists, indice, last_block_num)
                indice += 1
                last_block_num = block_num
                inv_index.clear()
                posting_lists.clear()

            if term not in inv_index:
                inv_index[term] = [1, block_num]  # [df, block_num]
                block_num += 1
                posting_lists.append({'next': -1, doc_id: score_tf(freq)})
            else:
                posting_lists[inv_index[term][1] - last_block_num][doc_id] = score_tf(freq)
                inv_index[term][0] += 1
    print(block_num, indice)
    return indice, block_num

def escrituraBlock(cantbloques, data, key1, key2):
    tam = len(data) - lista_tam
    with open(f"blocks/bloque{key1}.pkl", 'wb') as file:
        pickle.dump(dict(data[:len(data) - tam]), file)
    if tam > lista_tam:
        cantbloques += 1
        escrituraBlock(cantbloques, data, cantbloques, cantbloques + 1)
        return cantbloques

    with open(f"blocks/bloque{key2}.pkl", 'wb') as file:
        pickle.dump(dict(data[len(data) - tam:]), file)

    return cantbloques


def combined(result, key, elemento1, elemento2, cantbloques):
    # print("-------------------------->Enter", elemento1, elemento2)
    result[key][0] = elemento1[0] + elemento2[0]

    with open(f"blocks/bloque{elemento1[1]}.pkl", 'rb') as file:
        data1 = pickle.load(file)
    with open(f"blocks/bloque{elemento2[1]}.pkl", 'rb') as file:
        data2 = pickle.load(file)
    data1 = {**data1, **data2}

    data1 = list(data1.items())

    if len(data1) > lista_tam:
        cantbloques = escrituraBlock(cantbloques, data1, elemento1[1], elemento2[1])
    else:
        with open(f"blocks/bloque{elemento1[1]}.pkl", 'wb') as file:
            pickle.dump(dict(data1), file)
        os.remove(f"blocks/bloque{elemento2[1]}.pkl")

    result[key][1] = elemento1[1]
    return cantbloques

def borrar_archivos_previos():
    for elemento in os.listdir("indicesF"):
        elemento_r = os.path.join("indicesF", elemento)
        os.remove(elemento_r)

def print_all():
    i = 0
    while os.path.exists(f"indicesF/indice_invertido{i}.pkl"):
        with open(f"indicesF/indice_invertido{i}.pkl", "rb") as file:
            dic_ = pickle.load(file)
        print(f"i{i}", ":", dic_)
        i += 1

def merge_interno(espacio_act, indice_act, cantbloques):
    i = 0
    result = {}
    indice_archivos = 0
    while os.path.exists(f"indicesF/indice_invertido{indice_archivos}.pkl") and i < indice_act:
        # print("i", i)
        # input("")
        with open(f"indicesF/indice_invertido{i}.pkl", "rb") as file:
            dic_indic_disk = pickle.load(file)

        # print("Act1", espacio_act)
        # print("Act2", dic_indic_disk)
        while len(dic_indic_disk) != 0 and len(espacio_act) != 0:
            # print(espacio_act, "|", dic_indic_disk)
            key1 = next(iter(espacio_act))
            key2 = next(iter(dic_indic_disk))
            if key1 == key2:
                result[key1] = [0, 0]
                cantbloques = combined(result, key1, espacio_act[key1], dic_indic_disk[key2], cantbloques)
                espacio_act.pop(key1)
                dic_indic_disk.pop(key2)
            elif key1 < key2:
                result[key1] = [espacio_act[key1][0], espacio_act[key1][1]]
                espacio_act.pop(key1)
            else:
                result[key2] = [dic_indic_disk[key2][0], dic_indic_disk[key2][1]]
                dic_indic_disk.pop(key2)

        result = {**result, **espacio_act}
        result = {**result, **dic_indic_disk}

        espacio_act.clear()
        dic_indic_disk.clear()

        tam_block = os.path.getsize(f"blocks/bloque{result[next(iter(result))][1]}.pkl")

        espacio_act = {}

        for clave, valor in result.items():
            if len(pickle.dumps(espacio_act)) + tam_block < page_size:
                espacio_act[clave] = valor
            else:
                # print("Escrito", i, espacio_act)
                with open(f"indicesF/indice_invertido{i}.pkl", 'wb') as file:
                    pickle.dump(espacio_act, file)
                i += 1
                espacio_act.clear()
                espacio_act[clave] = valor

        indice_archivos += 1
        result.clear()
        # print("Sobrante", espacio_act, i)

    return i, espacio_act, cantbloques

def merge_blocks1(indices, cantbloques):
    borrar_archivos_previos()
    indice_act = 0

    while indice_act != indices:
        with open(f"indices/indice_invertido{indice_act}.pkl", "rb") as file:
            espacio1 = pickle.load(file)
        # print("Inicio", espacio1)
        indice_fin, espacio1, cantbloques = merge_interno(espacio1, indice_act, cantbloques)

        # print("---->", indice_fin, espacio1)
        with open(f"indicesF/indice_invertido{indice_fin}.pkl", "wb") as file:
            pickle.dump(espacio1, file)

        os.remove(f"indices/indice_invertido{indice_act}.pkl")
        indice_act += 1

    print_all()

def merge_blocks(indices):
    new_inv_idx = {}
    for i in range(indices):
        inv_index1 = {}
        with open(f"indices/indice_invertido{i}.pkl", "rb") as file:
            inv_index1 = pickle.load(file)
            json_index1 = json.dumps(inv_index1, indent=3)
        if os.path.exists(f"indices/indice_invertido{i}.pkl"):
            print("eiminando")
            os.remove(f"indices/indice_invertido{i}.pkl")
        print(i, ": \n", json_index1)
        for j in range(i):
            inv_index2 = {}
            with open(f"indices/indice_invertido{j}.pkl", "rb") as file:
                inv_index2 = pickle.load(file)
                json_index2 = json.dumps(inv_index2, indent=3)
            if os.path.exists(f"indices/indice_invertido{j}.pkl"):
                print("eiminando")
                os.remove(f"indices/indice_invertido{j}.pkl")
            print(j, ": \n", json_index2)
            w = 0
            for x in range(len(inv_index1.keys())):
                term1 = inv_index1.keys()[x]
                term2 = inv_index2.keys()[w]
                if term1 < term2:
                    new_inv_idx[term1] = inv_index1[term1]
                elif term1 > term2:
                    new_inv_idx[term2] = inv_index2[term2]
                    w += 1
                else:
                    new_inv_idx[term1] = [
                        inv_index1[term1][0] + inv_index2[term2][0],
                        inv_index2[term2][1]
                    ]
                    w += 1
                    bloque1 = inv_index1[term1][1]
                    bloque2 = inv_index2[term2][1]
                    postings1 = {}
                    postings2 = {}
                    with open(f"blocks/bloque{bloque1}", 'rb') as posting1, open(f"blocks/bloque{bloque2}", 'rb') as posting2:
                        postings1 = pickle.load(posting1)
                        postings2 = pickle.load(posting2)
                    print(postings1)
                    print(postings2)
                    del postings1['next']
                    postings3 = {**postings2, **postings1}


canciones = load_full_dataframe()
docs = canciones['processed_text'].tolist()
indices, cantbloques = generate_tfw(docs)
print(indices, cantbloques)
merge_blocks1(indices, cantbloques)
#
