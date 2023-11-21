import pickle

import math

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer

import nltk
nltk.download('stopwords')

stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))

stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = stemmer_spanish if "el" in tokens or "la" in tokens else stemmer_english
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

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
        with open('blocks/bloque' + next + '.pkl', 'rb') as blocks:
            dic_blocks = pickle.load(blocks)
        tam += len(dic_blocks)
        next = dic_blocks['next']
    return math.log10(cantDocuments, tam)

def binary_recollection(cantarchivos, word, cantDocuments):
    # indiceinvertido 0 -> 1
    # bloque 0 -> 1
    left = 0
    right = cantarchivos - 1
    while left <= right:
        half = (left + right) // 2
        with open('indices/indice_invertido' + half + '.pkl', 'rb') as mini_dic:
            dic_keys = pickle.load(mini_dic)

        if word in dic_keys:
            return dic_keys[word], get_idf(dic_keys['word'], cantDocuments)
        elif dic_keys.keys()[0] < word:
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
    print(query_frecuency)
    query = {}
    datos = []
    norm_query = 0
    for i in query_frecuency.keys():
        bloque, query_idf = binary_recollection(cantarchivos, i)
        if bloque != -1:
            datos.append(bloque)
            query[i] = query[i] * query_idf
            norm_query += (query[i] ** 2)

    norm_query = math.sqrt(norm_query)

    query_frecuency.clear()

    resultado = {}
    for i in range(cantDocuments):
        suma_dividendo = 0
        word = 0
        for j in query.keys():
            suma_dividendo += (query[j] * get_idf(datos[word], i))

        resultado[i] = (suma_dividendo / (norm_query * norma_doc[i]))

    resultado = dict(sorted(resultado.items(), key=lambda item: item[1], reverse=True))

    contador = 0
    topkDocuments = []
    for i in resultado.keys():
        topkDocuments.append(i)
        contador += 1
        if contador == topk:
            break

    return topkDocuments

# query = input("Ingresa la query: ")
# topK = int(input("Ingresa el topK: "))
#
# print(wtf_query(query))



