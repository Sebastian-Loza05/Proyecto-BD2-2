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

def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

def score_idf(N, df_t):
    return math.log10(N/df_t) if df_t > 0 else 0

def nested_defaultdict():
    return defaultdict(float)

def build_index(docs):
    inverted_index = defaultdict(list)
    N = len(docs)
    df = defaultdict(int)

    for doc_id, doc in enumerate(docs):
        terms = set(doc.split())
        for term in terms:
            inverted_index[term].append(doc_id)
            df[term] += 1

    idf_values = {term: score_idf(N, df_t) for term, df_t in df.items()}
    
    return inverted_index, idf_values

def cosine(query, block_num, num_docs, idf_values):
    with open(f"block_{block_num}.pkl", "rb") as file:
        inverted_index = pickle.load(file)

    processed_query = preprocess_text(query)
    query_terms = processed_query.split()
    query_tf = defaultdict(int)
    for term in query_terms:
        query_tf[term] += 1
    max_tf = max(query_tf.values())

    tf_idf_query = {}
    for term in query_terms:
        if term in idf_values:
            tf_q = 0.5 + 0.5 * (query_tf[term] / max_tf)
            tf_idf_query[term] = tf_q * idf_values[term]

    similarities = defaultdict(float)
    for term, weight in tf_idf_query.items():
        if term in inverted_index:
            for doc_id in inverted_index[term]:
                similarities[doc_id] += weight

    return similarities

def retrieve_top_k(query, k, num_blocks, num_docs, idf_values):
    overall_similarities = defaultdict(float)
    for block_num in range(num_blocks):
        block_similarities = cosine(query, block_num, num_docs, idf_values)
        for doc_id, score in block_similarities.items():
            overall_similarities[doc_id] += score

    top_k_indices = sorted(overall_similarities, key=overall_similarities.get, reverse=True)[:k]
    for idx in top_k_indices:
        print(f"Doc ID: {idx}, Terms: {docs[idx]}")
    return df.iloc[top_k_indices]

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = SnowballStemmer('english')
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)

def write_block_to_disk(inverted_index, block_num):
    with open(f"block_{block_num}.pkl", "wb") as file:
        pickle.dump(inverted_index, file)

BLOCK_SIZE = 4000
stop_words = set(stopwords.words('english'))

df = pd.read_csv('spotify.csv', on_bad_lines='skip')
df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
df['processed_text'] = df['combined_text'].apply(preprocess_text)
docs = df['processed_text'].tolist()
num_blocks = (len(docs) + BLOCK_SIZE - 1) // BLOCK_SIZE

inverted_index, idf_values = build_index(docs)

for i in range(num_blocks):
    start_idx = i * BLOCK_SIZE
    end_idx = min(start_idx + BLOCK_SIZE, len(docs))
    block_docs = docs[start_idx:end_idx]
    inverted_index_block, _ = build_index(block_docs)
    write_block_to_disk(inverted_index_block, i)

query_original = "Maluma and ozuna"
query = preprocess_text(query_original)
print(f"Query original: {query_original}")
print(f"Query procesado: {query}")
k = 5
num_docs = len(df)
top_k_results = retrieve_top_k(query, k, num_blocks, num_docs, idf_values)
print(top_k_results)
