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

page_size = 500
lista_tam = 19
stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')
cantidadDocs = 25
norma = []
CANT_INDICES = 0

def print_indice():
    global CANT_INDICES
    for i in range(CANT_INDICES):
        with open(f"indicesF/indice_invertido{i}.pkl", 'rb') as file:
            indice = pickle.load(file)
            indice_bonito = json.dumps(indice, indent=4)
        print(indice_bonito)


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
    borrar_archivos_previos()
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
    print("Cantidad de indices: ", indice)
    print(block_num, indice)
    return indice, block_num

def escrituraBlock(cantbloques, data, key1, key2):
    tam = len(data)
    result = {'next': -1}
    while tam > lista_tam:
        for key in data.keys():
            if key != 'next':
                if len(result) + 1 > lista_tam:
                    result['next'] = cantbloques
                    with open(f"blocks/bloque{key1}.pkl", 'wb') as file:
                        pickle.dump(result, file)
                    result.clear()
                    key1 = cantbloques
                    cantbloques += 1
                    result['next'] = -1
                    result[key] = data[key]
                    tam -= 1
                else:
                    result[key] = data[key]
                    tam -= 1

    with open(f"blocks/bloque{key1}.pkl", 'wb') as file:
        pickle.dump(result, file)
    if key1 == key2:
        print("Son igualesssssssssss")
    # os.remove(f"blocks/bloque{key2}.pkl")
    return cantbloques


def combined(result, key, elemento1, elemento2, cantbloques):
    # print("-------------------------->Enter", elemento1, elemento2)
    result[key] = [0, 0]
    result[key][0] = elemento1[0] + elemento2[0]

    with open(f"blocks/bloque{elemento1[1]}.pkl", 'rb') as file:
        data1 = pickle.load(file)
    with open(f"blocks/bloque{elemento2[1]}.pkl", 'rb') as file:
        data2 = pickle.load(file)
    data1 = {**data1, **data2}

    if len(data1) > lista_tam:
        cantbloques = escrituraBlock(cantbloques, data1, elemento1[1], elemento2[1])
    else:
        with open(f"blocks/bloque{elemento1[1]}.pkl", 'wb') as file:
            pickle.dump(data1, file)
        # os.remove(f"blocks/bloque{elemento2[1]}.pkl")

    result[key][1] = elemento1[1]
    return cantbloques

def borrar_archivos_previos():
    for elemento in os.listdir("indicesF"):
        elemento_r = os.path.join("indicesF", elemento)
        os.remove(elemento_r)

    for elemento in os.listdir("blocks"):
        elemento_r = os.path.join("blocks", elemento)
        os.remove(elemento_r)

    for elemento in os.listdir("indices"):
        elemento_r = os.path.join("indices", elemento)
        os.remove(elemento_r)

def print_all():
    i = 0
    while os.path.exists(f"indicesF/indice_invertido{i}.pkl"):
        with open(f"indicesF/indice_invertido{i}.pkl", "rb") as file:
            dic_ = pickle.load(file)
        print(f"i{i}", ":", dic_)
        i += 1

def merge_interno(espacio_act, indice_act, cantbloques):  # el primer índice, 0, 294
    i = 0
    result = {}
    indice_archivos = 0
    # print("Numero de indice: ", indice_act)
    # print("indice mergeando: ", espacio_act)
    while os.path.exists(f"indicesF/indice_invertido{indice_archivos}.pkl") and i < indice_act:
        # print("i", i)
        with open(f"indicesF/indice_invertido{i}.pkl", "rb") as file:
            dic_indic_disk = pickle.load(file)
        # print("indice_disco: ", dic_indic_disk)

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

def actualizar_tf_idf(N, norma):
    indice_archivos = 0
    while os.path.exists(f"indicesF/indice_invertido{indice_archivos}.pkl"):
        with open(f"indicesF/indice_invertido{indice_archivos}.pkl", "rb") as file:
            dic_indic_disk = pickle.load(file)

        for key, valor in dic_indic_disk.items():
            idf = score_idf(N, valor[0])
            dic_indic_disk[key][0] = idf
            actualizar_block(dic_indic_disk[key][1], idf, norma)

        with open(f"indicesF/indice_invertido{indice_archivos}.pkl", 'wb') as file:
            pickle.dump(dic_indic_disk, file)

        indice_archivos += 1

def merge_blocks1(indices, cantbloques, norma):
    indice_act = 0
    # print("indices: ", indices)

    while indice_act != indices:
        with open(f"indices/indice_invertido{indice_act}.pkl", "rb") as file:
            espacio1 = pickle.load(file)

        indice_fin, espacio1, cantbloques = merge_interno(espacio1, indice_act, cantbloques)
        # print("---->", indice_fin, espacio1)
        with open(f"indicesF/indice_invertido{indice_fin}.pkl", "wb") as file:
            pickle.dump(espacio1, file)

        os.remove(f"indices/indice_invertido{indice_act}.pkl")
        indice_act += 1

    norma = [0] * cantidadDocs
    actualizar_tf_idf(cantidadDocs, norma)
    norma = [math.sqrt(norma[i]) for i in range(cantidadDocs)]
    # print(norma)
    # print_all()

    global CANT_INDICES
    CANT_INDICES = indice_fin
    return norma, indice_fin

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

def get_idf(bloque, cantDocuments):
    tam = 0
    next = bloque
    while next != -1:
        # print("Next: ", next)
        with open('blocks/bloque' + str(next) + '.pkl', 'rb') as blocks:
            dic_blocks = pickle.load(blocks)
        tam += len(dic_blocks)
        next = dic_blocks['next']
    return math.log10(cantDocuments / tam)

def binary_recollection(cantarchivos, word, cantDocuments):
    # indiceinvertido 0 -> 1
    # bloque 0 -> 1
    left = 0
    right = cantarchivos - 1
    while left <= right:
        half = (left + right) // 2
        with open('indicesF/indice_invertido' + str(half) + '.pkl', 'rb') as mini_dic:
            dic_keys = pickle.load(mini_dic)

        if word in dic_keys:
            print(dic_keys)
            return dic_keys[word]
        elif next(iter(dic_keys)) < word:
            left = half + 1
        else:
            right = half - 1

    return -1, -1

def get_tfidf(bloque, i_doc):
    next = bloque
    while next != 1:
        with open('blocks/bloque' + next + '.pkl', 'rb') as blocks:
            dic_blocks = pickle.load(blocks)

        if i_doc in dic_blocks:
            return dic_blocks[i_doc]
        next = dic_blocks['next']

    return 0

def documentos_topK(query, topk, cantarchivos, cantDocuments, norma_doc):
    query_frecuency = wtf_query(query)
    norm_query = 0
    for i in query_frecuency.keys():
        idf_palabra_bloque = binary_recollection(cantarchivos, i, cantDocuments)
        query_frecuency[i] = [query_frecuency[i] * idf_palabra_bloque[0], idf_palabra_bloque[1]]
    print("query:", query_frecuency)

    docs = {}
    for key in query_frecuency.keys():
        norm_query += query_frecuency[key][0]**2
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
        docs[key] = (math.sqrt(docs[key])) / (math.sqrt(norm_query) * math.sqrt(norma_doc[key]))

    print("---", docs)
    resultado = dict(sorted(docs.items(), key=lambda item: item[1]))

    contador = 0
    topkDocuments = []
    for i in resultado.keys():
        topkDocuments.append(i)
        contador += 1
        if contador == topk:
            break

    return topkDocuments


canciones = load_full_dataframe()
docs = canciones['processed_text'].tolist()
indices, cantbloques = generate_tfw(docs)
print("->", indices, cantbloques)
norma, indicesF = merge_blocks1(indices, cantbloques, norma)
print("-->", indicesF)
print("Indices")
print_indice()
print(documentos_topK("los lobos no podian distinguir la noche", 10, indicesF, cantidadDocs, norma))
#
