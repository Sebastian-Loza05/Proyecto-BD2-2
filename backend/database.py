import psycopg2
import time

def connect():
    return psycopg2.connect(
        host="localhost",
        database="BD2Proyecto2",
        user="postgres",
        port=5432,
        password="utec"
    )

def search(conn, Q, k):
    cur = conn.cursor()
    query = Q.split(" ")
    query = '|'.join(query)

    cur.execute(f"""
        SELECT track_artist, track_name, lyrics, ts_rank_cd(full_text, query, 1) AS rank
        FROM songslist, to_tsquery('english', '{query}') query
        WHERE query @@ full_text
        ORDER BY rank ASC
        LIMIT {k};
    """)

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  # Esto obtiene los nombres de las columnas
    result = [dict(zip(columns, row)) for row in rows]  # Esto convierte las filas en diccionarios

    cur.close()
    
    return result