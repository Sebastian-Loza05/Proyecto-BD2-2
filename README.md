# Proyecto-BD2-2

## Introducción

### Objetivos
El principal objetivo de este proyecto es implementar y entender el funcionamiento del índice invertido usando el modelo de recuperación por ranking para consultas de texto libre. Con esto, esperamos mejorar la velocidad y eficiencia de las búsquedas en grandes conjuntos de datos.

### Objetivos Específicos:
-  Construir óptimamente un Índice Invertido para tareas de búsqueda y recuperación en documentos de texto
-  Construir una estructura multidimensional para dar soporte a las búsqueda y recuperación eficiente de imágenes / audio usando vectores característicos.
### Descripción del dominio de datos y la importancia de aplicar indexación
Utilizamos un dataset proporcionado en formato de tabla, que contiene información sobre canciones disponibles en Spotify. Cada fila de la tabla se compone de múltiples campos textuales que se concatenan para formar un solo texto. Nuestro dataset de Spotify incluye campos como track_id, track_name, track_artist, lyrics, track_popularity, entre otros. Por ejemplo:
```
track_id: 0017A6SJgTbfQVU2EtsPNo
track_name: Pangarap
track_artist: Barbie's Cradle
lyrics: Minsan pa Nang ako'y napalingon...
track_popularity: 41
track_album_name: Trip
playlist_name: Pinoy Classic Rock
...
```
Sin indexación, una consulta de búsqueda requeriría escanear cada documento en la base de datos, lo que sería altamente ineficiente en conjuntos de datos grandes. El índice invertido, en particular, es beneficioso ya que proporciona una estructura de datos optimizada para consultas de texto libre.

## Backend: Índice Invertido
El código presentado es para construir un índice invertido para un conjunto de documentos, en este caso, canciones de Spotify, utilizando el algoritmo SPIMI (Single-pass in-memory indexing). Se usan las principales librerías
```
import math
import pickle
import os
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```
### Preprocesamiento de texto
Se establecen stopwords en inglés y español, además de stemmers para procesar el texto y dejarlo en un formato estandarizado. La función preprocess_text lleva a cabo este proceso.
```
stop_words = set(stopwords.words('english')).union(set(stopwords.words('spanish')))
block_num = 0
stemmer_english = SnowballStemmer('english')
stemmer_spanish = SnowballStemmer('spanish')

def preprocess_text(text):
    text = ' '.join([word for word in word_tokenize(text) if word.isalpha()])
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.lower() not in stop_words]
    stemmer = stemmer_spanish if "el" in tokens or "la" in tokens else stemmer_english
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    return ' '.join(stemmed_tokens)
```

### SPIMI
La función spimi_invert construye índices invertidos en bloques utilizando el algoritmo SPIMI. Esta función toma como entrada la lista de documentos y, para cada documento, construye una lista de términos (o tokens) y su frecuencia de aparición. Los bloques de índice invertido se escriben en el disco cuando se alcanza un límite específico de memorias definido por page_size.
```
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
    return indice
```
