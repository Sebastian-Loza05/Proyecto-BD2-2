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

El código está [aquí](/backend/indiceInvertido.py#generate-tfw-docs)

### Merge
Para el merge se realizan distintas operaciones separadas en distintas funciones (*merge()*, *merge_interno()*, *combine_indices()*, *combine_blocks()*, *actualizar_tf_idf()*, *actualizar_block()*)
- Merge()
  
  Esta función va a ejecutarse mientras hayan bloques sin mergearse. Es decir, mientras existan archivos dentro de nuestra carpeta "indices" se llamará a una función *merge_interno()*. Uana vez que se termine de mergearse, se tendrá en nuestra carpeta final a los bloques que contienen a nuestro índice ya mergeado y se empezará a crear la norma a su vez que se actualizarán los valores idf final para cada token ya que ya se tiene un índice con todos los tokens y que se repiten una sóla vez y con su valor final del df (document frequency), esto se hará en *actualizar_tf_idf(norma)*. Puedes encontrar el código [aquí](/backend/indiceInvertido.py#merge)
- merge_interno()

  Esta es una de las funciones principales. Aquí se mergeará a todos los índices ya mergeados con el nuevo índice sin mergear para el cuál se ha llamado esta función. Se recorrerá a todos los archivos en la carpeta de índices mergeados y al mergearse se escribirán dentro de otra carpeta auxiliar dnde se escribirá el resultado, cuando esta función sea llamada nuevamente la carpeta de índices mergeados será esta carpeta auxiliar y se usará como auxiliar a la carpeta que antes fue la carpeta de índices mergeados, y así se intercalará en cada llamada a la función. Esta función usa la lógica normal para mergear 2 diccionarios, pero cuando encuentra tokens que son iguales, tiene que usar una lógica un poco más compleja para también mergear a los bloques que tienen asociados cada uno. A su vez que va verifiando si el tamaño del indice local, más el tamaño de un bloque de posting lists supera el tamaño máximo permitido por la RAM y se escribe en el bloque auxiliar. Puedes encontrar el código [aquí](/backend/indiceInvertido.py#merge-interno)
- combine_indices()

  En esta función se se combinan ls bloques de las postings list de un token que se ha combinado en el mergeo de nuestro índice invertido, en caso se sobrapase el límite permitido en una posting list, se escribe en memoria secundaria y se encadena un nuevo bloque para así poder seguir ingresando los postings/documentos correspondientes al token que se ha mergeado, esto se hace en la función *combine_blocks()*. Puedes encontrar el código [aquí](/backend/indiceInvertido.py#combine-indices)

- actualizar_tf_idf()

  En esta función se leeran todos los bloques en memoria secundaria y se irán actualizando el valor idf y se pondrá en la primera posición de la lista que representa al value de cada token. Seguido de eso se llamará a una función *actualizar_bloque(num_bloque, idf, norma)* para cada token. Puedes encontrar el código [aquí](/backend/indiceInvertido.py#actualizar-tf-idf)

- actualizar_bloque()

  Esta es una función recursiva que abrirá a todos los bloques encadenados asociados al token para el que fue llamado la función y se actualizará el valor de tf para cada documento asociado a ese token en ese bloque con el valor de tf*idf y se volverá a escribir en en el mismo archivo. También se irá calculando el valor para la norma de cada documento. Puedes encontrar el código [aquí](/backend/indiceInvertido.py#actualizar-block)


### Similitud Coseno
Para la similitud por coseno usamos la función *binary-recollection()* para cada token perteneciente a la consulta textual. Para esto previamente hemos calculado los valores tf-suavizados de ls términos de la query. El *binary_recollection()* nos ayuda a obtener los número de bloques de los tokens haciendo una búsqueda binaria en el índice invertido en memora secundaria para así no traer todos los bloques a la RAM. Luego de haber obtenido los número de bloques de cada término de la query en el índice invertido podemos leerlos y con el tf-idf que tenemos guardado y con los valores de la norma, de cada documento aplicamos la fórmula de la similitud de coseno: 
![cosine](data:image/png;base64,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)

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

