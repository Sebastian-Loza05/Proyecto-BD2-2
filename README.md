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

## Backend
### Índice Invertido
El código presentado es para construir un índice invertido para un conjunto de documentos, en este caso, canciones de Spotify, utilizando el algoritmo SPIMI (Single-pass in-memory indexing). Se usan las principales librerías
```python
import math
import pickle
import os
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```
### Preprocesamiento de texto
Se establecen stopwords en inglés y español, además de stemmers para procesar el texto y dejarlo en un formato estandarizado. La función preprocess_text lleva a cabo este proceso. La función devuelve el texto preprocesado como una cadena de caracteres con tokens separados por espacios. Se aplica Stemming que es una técnica de procesamiento del lenguaje natural que se utiliza para reducir las palabras a su raíz o forma base. Por ejemplo, "running" se convierte en "run". 
```python
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
La función spimi_invert construye índices invertidos en bloques utilizando el algoritmo SPIMI. La función generate_tfw(docs) toma como entrada la lista de documentos y, para cada documento, construye una lista de términos (o tokens) para construir in primer índice que sólo tendrá las frecuencias de los términos en cada documento. Para esto hace lo siguiente:
- Para cada documento, se cuentan las ocurrencias de cada término usando la clase Counter.
- Luego, para cada término y su frecuencia en el documento:
  
Se agrega el término a un diccionario inv_index con la key como el término y su value una lista que tiene 2 valores: El df (frecuencia de documento) y el num_bloque (el num de bloque donde estará su posting list), además que se agrega  a su posting list que es un diccionario el id del documento y tf_suavizado respectivo. En el caso ocurra que agregar este nuevo término al inv_index hace que se supere el límite de RAM disponible para el índice no se agrega y se escribe en memoria secundaria.

En caso el término ya pertenezca al índice invertido se agrega el nuevo documento al posting list y se aumenta el df del término.
  
Al final de la función, se devuelve la cantidad de bloques escritos en memoria secundaria.

El código está [aquí](generate-tfw-docs)

### Merge
Para el merge se realizan distintas operaciones separadas en distintas funciones (*merge()*, *merge_interno()*, *combine_indices()*, *combine_blocks()*, *actualizar_tf_idf()*, *actualizar_block()*)
- Merge()
  
  Esta función va a ejecutarse mientras hayan bloques sin mergearse. Es decir, mientras existan archivos dentro de nuestra carpeta "indices" se llamará a una función *merge_interno()*. Uana vez que se termine de mergearse, se tendrá en nuestra carpeta final a los bloques que contienen a nuestro índice ya mergeado y se empezará a crear la norma a su vez que se actualizarán los valores idf final para cada token ya que ya se tiene un índice con todos los tokens y que se repiten una sóla vez y con su valor final del df (document frequency), esto se hará en *actualizar_tf_idf(norma)*.
- merge_interno()

  Esta es una de las funciones principales. Aquí se mergeará a todos los índices ya mergeados con el nuevo índice sin mergear para el cuál se ha llamado esta función. Se recorrerá a todos los archivos en la carpeta de índices mergeados y al mergearse se escribirán dentro de otra carpeta auxiliar dnde se escribirá el resultado, cuando esta función sea llamada nuevamente la carpeta de índices mergeados será esta carpeta auxiliar y se usará como auxiliar a la carpeta que antes fue la carpeta de índices mergeados, y así se intercalará en cada llamada a la función. Esta función usa la lógica normal para mergear 2 diccionarios, pero cuando encuentra tokens que son iguales, tiene que usar una lógica un poco más compleja para también mergear a los bloques que tienen asociados cada uno. A su vez que va verifiando si el tamaño del indice local, más el tamaño de un bloque de posting lists supera el tamaño máximo permitido por la RAM y se escribe en el bloque auxiliar.
- combine_indices()

  En esta función se se combinan ls bloques de las postings list de un token que se ha combinado en el mergeo de nuestro índice invertido, en caso se sobrapase el límite permitido en una posting list, se escribe en memoria secundaria y se encadena un nuevo bloque para así poder seguir ingresando los postings/documentos correspondientes al token que se ha mergeado.

- actualizar_tf_idf()

  En esta función se leeran todos los bloques en memoria secundaria y se irán actualizando el valor idf y se pondrá en la primera posición de la lista que representa al value de cada token. Seguido de eso se llamará a una función *actualizar_bloque(num_bloque, idf, norma)* para cada token.

- actualizar_bloque()

  Esta es una función recursiva que abrirá a todos los bloques encadenados asociados al token para el que fue llamado la función y se actualizará el valor de tf para cada documento asociado a ese token en ese bloque con el valor de tf*idf y se volverá a escribir en en el mismo archivo. También se irá calculando el valor para la norma de cada documento.


### Similitud Coseno
El método score_documents toma como parámetros una consulta (query) y un índice invertido fusionado (merged_index). Luego, se divide la consulta en términos individuales y se inicializa un diccionario doc_scores para almacenar los scores de los documentos. Para cada término en la consulta, si el término está en el índice invertido, se itera a través de las listas de publicación (documentos que contienen el término) y se acumula el valor de TF-IDF para ese término en el score del documento.
Luego, se normaliza el score del documento dividiendo el score acumulado por la longitud del documento. Finalmente, se multiplica el score del documento por la cantidad de términos de la consulta que coinciden con el documento. Esto es un factor adicional para aumentar el score de los documentos que contienen más términos de la consulta.

### Estructura y Ejecución del índice
![Estructura y Ejecución del índice](info-retrieval/public/indice.jpeg)
### Indice en PostgresSQL
- Se crea una tabla llamada songslist con múltiples campos, que incluyen detalles de la canción, el álbum, la lista de reproducción, características de la canción y más.
Población de Datos:

- Se usa el comando COPY para insertar datos de un archivo CSV (spotify.csv) en la tabla songslist.
Columna combined_text:

- Se añade una columna llamada combined_text, que combinara el contenido de todas las otras columnas en una sola columna de texto.
Conversión a tsvector:

- La columna full_text se crea y se rellena con el contenido de combined_text convertido a tsvector. El tipo tsvector es un tipo de datos específico de PostgreSQL utilizado para representar documentos en un formato que se puede buscar con índices invertidos. Aquí, setweight se usa para asignar un peso específico a los vectores, lo que puede influir en la clasificación de los resultados de búsqueda.
- Creación del Índice:

    - Se crea un índice usando la extensión gin (Generalized Inverted Index) en la columna combined_text. Esto permite búsquedas rápidas de texto completo en la columna combined_text

La función de búsqueda toma una consulta Q y un número k para devolver los k resultados superiores basados en la coincidencia de texto completo. La consulta se divide y se reformatea para adaptarse a la función to_tsquery. La consulta SQL busca coincidencias en la columna full_text y devuelve artistas, nombres de canciones y una puntuación de coincidencia (rank).

### MFCC
Para la obtención de los vectores característicos que representen a cada canción que indexaremos, usamos los Coeficientes Cepstrales de las frecuencias de Mel (MFCC). Normalmente se usan 13 coeficientes, ya que empíricamente se ha determinado que es la cantidad recomendable para una buena presición en la extracción de las características. Sin embargo, nosotros usaremos 20, ya que para la extracción de características en música es recomendable usar más coeficientes, cómo mínimo 20.

### Rtree
Usamos la librería rtree de python. Para esto necesitamos los puntos que serían los vectores característcos de las canciones que vamos a indexar, pero todos deben de tener la misma dimensión. El rtrre en python debe tener ciertas características como los archivos en los que se va a escribir el índice, la dimensión, etc.
```python
def create_indexRtree(mfccs_vector=None):
    prop = index.Property()
    prop.dimension = 20
    prop.buffering_capacity = 2 * 20
    prop.storage = index.RT_Disk
    prop.overwrite = False
    if os.path.exists("puntos.dat") and os.path.exists("puntos.idx"):
        idx = index.Rtree('puntos', properties=prop)
        return idx
    prop.dat_extension = 'dat'
    prop.idx_extension = 'idx'
    indx = index.Index('puntos', properties=prop)
    for i, p in enumerate(mfccs_vector):
        indx.insert(i, p)
    return indx

```
![Rtree](https://media.geeksforgeeks.org/wp-content/uploads/20190412142437/R-tree.png)

En este caso mfccs_vector es una lista con todos los puntos que vamos a ingresar y en el caso de que nuestro índice ya esté creado este parámetro sería None ya que el índice rtree sería cargado de los archivos. La dimensión es 20 al igual que la de los vectores que vamos a indexar. Definimos que el índice se va a guardar en el disco y q no se va a sobreescribir. Como nosotros construiremos el índice sólo una vez, no es muy importante el valor del buffering capacity ya que este sólo influirá en el rendimineto de la construcción del índice al insertar todos los valores.

### KNN-HighD

#### IndexLSK
##### Caracteristicas
 **Alta velocidad:** 
- **Uso de funciones Hash:** 

##### Ventajas

##### Desventajas

##### Funcionamiento interno

### FLASK API
El archivo views.py es una parte central de la aplicación Flask que se encarga de definir y manejar las rutas o endpoints a los que se puede acceder. Estos endpoints permiten realizar con un índice invertido y una base de datos PostgreSQL. 
Importaciones:
- Flask: Se importan las funciones request y jsonify de Flask. request permite acceder a los datos enviados por el cliente, mientras que jsonify facilita la devolución de respuestas en formato JSON.
- app: Se importa la instancia de Flask (app) desde el módulo app.
- indice: Este módulo contiene funciones relacionadas con el índice invertido.
- database: Este módulo tiene funciones para interactuar con una base de datos PostgreSQL.
La conexión a PostgresSQL se hace usando Pyscopg2
```
import psycopg2
import time
conn = psycopg2.connect(
    host="localhost",
    database="BD2Proyecto2",
    user=
    port = 5432,
    password=

cur = conn.cursor()
```
Endpoints:
```
@app.route('/invert_index', methods=['POST'])
def invert_index():
    query_text = request.json.get('query_text')
    top_k = int(request.json.get('top_k'))
    query_processed = indice.preprocess_text(query_text)
    results = indice.retrieve_top_k(query_processed, top_k, indice.merged_index, indice.num_docs)
    results_list = results.to_dict(orient='records')
    print("Llamado a Indice") 
    return jsonify(results_list)
```
Este endpoint espera una petición POST con un cuerpo que contiene un query_text y un top_k. Primero, se procesa el query_text utilizando la función preprocess_text del módulo indice. Luego, se llama a la función retrieve_top_k del mismo módulo para obtener los top_k resultados más relevantes. Los resultados se convierten a un formato de lista de diccionarios. Finalmente, se devuelve la lista de resultados en formato JSON.

Ruta de PostgreSQL:
```
@app.route('/psql', methods=['POST'])
def psql():
    data = request.get_json()
    query = data["query_text"]
    top_k = int(data["top_k"])

    conn = database.connect() 
    results = database.search(conn, query, top_k)  
    conn.close()
    print("Llamado a PSQL") 
    return jsonify(results)
```
Este endpoint también espera una petición POST con un cuerpo que contiene un query_text y un top_k. Se establece una conexión con la base de datos utilizando la función connect del módulo database. Se utiliza la función search del módulo database para buscar en la base de datos y obtener resultados. Una vez obtenidos los resultados, se cierra la conexión con la base de datos. Los resultados se devuelven en formato JSON.

Prueba en postman:
![Estructura y Ejecución del índice](info-retrieval/public/consulta.png)

## FrontEnd
![Estructura y Ejecución del índice](info-retrieval/public/front.png)

![Estructura y Ejecución del índice](info-retrieval/public/front2.png)

