import math
import pickle
import os
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pandas as pd
from itertools import islice

TERMS_LIMIT = 1000
stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')


def print_first_n_terms(n):
    with open("blocks/merge.pkl", "rb") as file:
        merged_index = pickle.load(file)

    first_n_terms = list(islice(merged_index.keys(), n))
    for term in first_n_terms:
        print(term)

def load_full_dataframe():
    df = pd.read_csv('spotify.csv', on_bad_lines='skip')
    df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
    df['processed_text'] = df['combined_text'].apply(preprocess_text)
    return df

def load_light_dataframe():
    return pd.read_csv('spotify.csv', usecols=['track_name','track_artist','track_id','lyrics'], on_bad_lines='skip')

def delete_all_blocks():
    """Función para borrar todos los archivos en la carpeta 'blocks'."""
    for root, dirs, files in os.walk('blocks'):
        for file in files:
            os.remove(os.path.join(root, file))

if not os.path.exists('blocks'):
    os.makedirs('blocks')
    
if not os.path.exists("blocks/merge.pkl"):
    delete_all_blocks()

def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

def score_idf(N, df_t):
    return math.log10(N/(1+df_t))

def write_block_to_disk(inverted_index, block_num):
    sorted_index = dict(sorted(inverted_index.items()))
    with open(f"blocks/block_{block_num}.pkl", "wb") as file:
        pickle.dump(sorted_index, file)

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = stemmer_spanish if "el" in tokens or "la" in tokens else stemmer_english
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def spimi_invert(docs):
    print("Aplicando algoritmo SPIMI...")
    global block_num
    inverted_index = defaultdict(dict)
    unique_terms = set()

    for doc_id, doc in enumerate(docs):
        terms = doc.split()
        term_freq = defaultdict(int)

        for term in terms:
            term_freq[term] += 1

        for term, tf in term_freq.items():
            if term not in inverted_index:
                if len(unique_terms) >= TERMS_LIMIT:
                    write_block_to_disk(inverted_index, block_num)
                    block_num += 1
                    inverted_index.clear()
                    unique_terms.clear()
                unique_terms.add(term)

            if doc_id not in inverted_index[term]:
                inverted_index[term][doc_id] = {'tf': tf, 'tf-idf': 0}  

    if inverted_index:
        write_block_to_disk(inverted_index, block_num)


def merge_blocks(num_blocks, num_docs):
    print("HACIENDO MERGE DE BLOCKS...")
    merged_index = defaultdict(dict)
    df = defaultdict(int)  # Frecuencia de documentos por término

    for block_num in range(num_blocks):
        with open(f"blocks/block_{block_num}.pkl", "rb") as file:
            block_index = pickle.load(file)
        for term, postings_dict in block_index.items():
            df[term] += len(postings_dict)
            if term not in merged_index:
                merged_index[term] = {"docs": dict(), "idf": 0}
            for doc_id, doc_data in postings_dict.items():
                if doc_id not in merged_index[term]["postings"]:
                    merged_index[term]["postings"][doc_id] = {
                        'tf': doc_data['tf'], 
                        'tf-idf': 0  
                    }

    # Calculando IDF para cada término y almacenando en el índice invertido
    for term, postings_dict in merged_index.items():
        idf = score_idf(num_docs, df[term])
        merged_index[term]["idf"] = idf
        for doc_id, doc_data in postings_dict["postings"].items():
            tf = doc_data['tf']
            doc_data['tf-idf'] = tf * idf

    with open("blocks/merge.pkl", "wb") as file:
        pickle.dump(merged_index, file)


def retrieve_top_k(query, k, merged_index, num_docs):
    print("OBTENIENDO TOP-K...")
    doc_scores = score_documents(query, merged_index)
    top_k_indices = sorted(doc_scores, key=doc_scores.get, reverse=True)[:k]
    return df.iloc[top_k_indices][['track_id', 'track_name', 'track_artist','lyrics']]


def score_documents(query, merged_index):
    print("APLICANDO COSINE...")
    query_terms = query.split()
    doc_scores = defaultdict(float)

    for term in query_terms:
        if term in merged_index:
            for doc_id, doc_data in merged_index[term]["postings"].items():  
                doc_weight = doc_data['tf-idf']
                doc_scores[doc_id] += doc_weight

    for doc_id, score in doc_scores.items():
        doc_length = sum([doc_data['tf-idf']**2 for term in merged_index if doc_id in merged_index[term]["postings"]])**0.5  
        if doc_length > 0:
            doc_scores[doc_id] /= doc_length

        terms_matched = sum([1 for term in query_terms if term in merged_index and doc_id in merged_index[term]["postings"]])  
        doc_scores[doc_id] *= terms_matched

    return doc_scores


if not os.path.exists("blocks/merge.pkl"):
    print("Creando índice invertido...")
    df = load_full_dataframe()
    docs = df['processed_text'].tolist()
    spimi_invert(docs)
    num_docs = len(docs)
    merge_blocks(block_num, num_docs)
    with open("blocks/merge.pkl", "rb") as file:
        merged_index = pickle.load(file)
else:
    print("Abriendo índice creado...")
  
    df = load_light_dataframe()  
    with open("blocks/merge.pkl", "rb") as file:
        merged_index = pickle.load(file)
    num_docs = sum([len(postings) for postings in merged_index.values()]) 

query_original = "cancion de calvin harris blame"
query = preprocess_text(query_original)

print("Primeros 20 Terminos del indice: ")
print_first_n_terms(20)

print("\nEstructura del indice:") #Postings -> Numero posicion de Fila del csv Por ejemplo abrazadito: {'postings': {12: {'tf': 4, 'tf-idf': 15.15587704622207}, ... Linea 12 que es todo un documento abrazadito tiene el score tf: 4 y tf-idf 15.5 respecto a esa fila 12.
first_key = next(iter(merged_index))
print(f"{first_key}: {merged_index[first_key]}")

print(f"\nQuery original: {query_original}")
print(f"Query procesado: {query}")
k = 10
top_k_results = retrieve_top_k(query, k, merged_index, num_docs)
print(top_k_results)
