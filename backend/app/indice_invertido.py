import pandas as pd
import nltk
import math
import numpy as np
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pickle
import os

nltk.download('stopwords')
nltk.download('punkt')

# Funciones para calcular TF-IDF y similitud de coseno
def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

def score_idf(N, df_t):
    return math.log10(N/df_t) if df_t > 0 else 0

def build_index(docs):
    inverted_index = defaultdict(list)  # La clave es un término y el valor es una lista de frecuencias de documentos
    for doc_id, doc in enumerate(docs):
        terms = doc.split()  
        term_freq = defaultdict(int)
        for term in terms:
            term_freq[term] += 1
        for term, freq in term_freq.items():
            inverted_index[term].append(freq)
    return inverted_index


#Guarda un bloque del índice invertido en el disco.
def write_block_to_disk(inverted_index, block_num):

    with open(f"block_{block_num}.pkl", "wb") as file:
        pickle.dump(inverted_index, file)

def cosine(query, num_blocks, num_docs):
    processed_query = preprocess_text(query)
    query_vector = build_index([processed_query])
    terms_in_query = list(query_vector.keys())
    tf_idf_query = []
    for term in terms_in_query:
        tf_value = score_tf(query_vector[term][0])
        idf_value = score_idf(num_docs, len(query_vector[term]))
        tf_idf_query.append(tf_value * idf_value)
    tf_idf_query = np.array(tf_idf_query)
    
    similarities = np.zeros(num_docs)
    for i in range(num_blocks):
        with open(f"block_{i}.pkl", "rb") as file:
            block_index = pickle.load(file)   
            for doc_id in range(num_docs):
                doc_vector_list = []
                for term in terms_in_query:
                    if term in block_index:
                        if doc_id < len(block_index[term]):
                            tf_value = score_tf(block_index[term][doc_id])
                        else:
                            tf_value = 0
                        idf_value = score_idf(num_docs, len(block_index[term]))
                        doc_vector_list.append(tf_value * idf_value)
                    else:
                        doc_vector_list.append(0)
                doc_vector = np.array(doc_vector_list)
                dot_product = np.dot(tf_idf_query, doc_vector)
                norm_query = np.linalg.norm(tf_idf_query)
                norm_doc = np.linalg.norm(doc_vector)
                similarity = dot_product / (norm_query * norm_doc) if (norm_query != 0 and norm_doc != 0) else 0
                
                index_to_assign = i * BLOCK_SIZE + doc_id
                if index_to_assign < num_docs:
                    similarities[index_to_assign] = similarity

    return similarities

def retrieve_top_k(query, k, num_blocks, num_docs):
    similarities = cosine(query, num_blocks, num_docs)
    top_k_indices = similarities.argsort()[-k:][::-1]
    return df.iloc[top_k_indices]

def preprocess_text(text):
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stopwords.words('spanish')]
    stemmer = SnowballStemmer('spanish')
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def build_vocabulary(docs):
    vocabulary = set()
    for doc in docs:
        terms = doc.split()
        vocabulary.update(terms)
    return list(vocabulary)

BLOCK_SIZE = 4000
# Carga de dataset

df = pd.read_csv('styles.csv', on_bad_lines='skip')

# Concatenar campos textuales
df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
# Aplicar preprocesamiento
df['processed_text'] = df['combined_text'].apply(preprocess_text)
docs = df['processed_text'].tolist()
num_blocks = (len(docs) + BLOCK_SIZE - 1) // BLOCK_SIZE

# Creación de bloques y escritura en disco
for i in range(num_blocks):
    start_idx = i * BLOCK_SIZE
    end_idx = min(start_idx + BLOCK_SIZE, len(docs))
    block_docs = docs[start_idx:end_idx]
    inverted_index = build_index(block_docs)
    write_block_to_disk(inverted_index, i)

query = "Men's Blue Shirts"
k = 3
num_docs = len(df)
vocabulary = build_vocabulary(docs)
top_k_results = retrieve_top_k(query, k, num_blocks, num_docs)
print(top_k_results)