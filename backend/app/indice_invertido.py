import math
import pickle
from collections import defaultdict
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
import pandas as pd
import os

TERMS_LIMIT = 1000
stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')

os.system('del block_*.pkl')

def score_tf(tf):
    return 1 + math.log10(tf) if tf > 0 else 0

def score_idf(N, df_t):
    return math.log10(N/(1+df_t)) # Suavización añadida al IDF

def write_block_to_disk(inverted_index, block_num):
    with open(f"block_{block_num}.pkl", "wb") as file:
        pickle.dump(inverted_index, file)

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    
    # Determine main language of text for stemming (simple heuristic)
    stemmer = stemmer_spanish if "el" in tokens or "la" in tokens else stemmer_english
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    return ' '.join(stemmed_tokens)

def spimi_invert(docs):
    global block_num
    inverted_index = defaultdict(list)
    unique_terms = set()

    for doc_id, doc in enumerate(docs):
        terms = doc.split()
        for term in terms:
            if term not in inverted_index:
                if len(unique_terms) >= TERMS_LIMIT:
                    write_block_to_disk(inverted_index, block_num)
                    block_num += 1
                    inverted_index.clear()
                    unique_terms.clear()
                unique_terms.add(term)
            inverted_index[term].append(doc_id)

    if inverted_index:
        write_block_to_disk(inverted_index, block_num)

def calculate_idf_values(num_docs, num_blocks):
    df = defaultdict(int)

    for block_num in range(num_blocks):
        with open(f"block_{block_num}.pkl", "rb") as file:
            block_index = pickle.load(file)
        for term, postings_list in block_index.items():
            df[term] += len(set(postings_list))

    idf_values = {term: score_idf(num_docs, df_t) for term, df_t in df.items()}
    
    return idf_values

def retrieve_top_k(query, k, num_blocks, num_docs, idf_values):
    overall_similarities = defaultdict(float)
    for block_num in range(num_blocks):
        block_similarities = cosine(query, block_num, num_docs, idf_values)
        for doc_id, score in block_similarities.items():
            overall_similarities[doc_id] += score

    top_k_indices = sorted(overall_similarities, key=overall_similarities.get, reverse=True)[:k]
    return df.iloc[top_k_indices]

def cosine(query, block_num, num_docs, idf_values):
    with open(f"block_{block_num}.pkl", "rb") as file:
        block_index = pickle.load(file)

    query_terms = query.split()
    doc_scores = defaultdict(float)

    for term in query_terms:
        if term in block_index:
            idf = idf_values.get(term, 0)
            query_weight = idf  # Peso TF-IDF de la consulta
            for doc_id in block_index[term]:
                tf = block_index[term].count(doc_id)
                doc_weight = score_tf(tf) * idf
                doc_scores[doc_id] += doc_weight * query_weight  # Similitud del coseno como producto punto

    # Normalización (division por norma L2)
    for doc_id, score in doc_scores.items():
        doc_length = sum([score_tf(block_index[term].count(doc_id))**2 for term in block_index if doc_id in block_index[term]])**0.5
        if doc_length > 0:
            doc_scores[doc_id] /= doc_length

    # Bono por coincidencia de múltiples términos
    for doc_id in doc_scores:
        terms_matched = sum([1 for term in query_terms if term in block_index and doc_id in block_index[term]])
        doc_scores[doc_id] *= terms_matched

    return doc_scores

df = pd.read_csv('spotify.csv', on_bad_lines='skip')
df['combined_text'] = df.apply(lambda row: ' '.join(row.astype(str)), axis=1)
df['processed_text'] = df['combined_text'].apply(preprocess_text)
docs = df['processed_text'].tolist()

spimi_invert(docs)

idf_values = calculate_idf_values(len(df), block_num)

query_original = "My Nigga,YG"
query = preprocess_text(query_original)
print(f"Query original: {query_original}")
print(f"Query procesado: {query}")
k = 10
num_docs = len(df)
top_k_results = retrieve_top_k(query, k, block_num, num_docs, idf_values)
print(top_k_results)
