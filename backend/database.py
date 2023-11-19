import psycopg2
import time
from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("HOST_DB")
DATABASE = os.getenv("DATABASE_NAME")
USER = os.getenv("USER_DB")
PORT = os.getenv("PORT")
PASSWORD = os.getenv("PASSWORD_DB")
print(USER)

def connect():
    return psycopg2.connect(
        host=HOST,
        database=DATABASE,
        user=USER,
        port=PORT,
        password=PASSWORD
    )

def search(conn, Q, k):
    cur = conn.cursor()
    query = Q.split(" ")
    query = '|'.join(query)

    cur.execute(f"""
        SELECT track_artist, track_name, lyrics, ts_rank_cd(full_text, query, 1) AS rank
        FROM songslist, to_tsquery('english', '{query}') query
        WHERE query @@ full_text
        ORDER BY rank DESC
        LIMIT {k};
    """)

    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]  # Esto obtiene los nombres de las columnas
    result = [dict(zip(columns, row)) for row in rows]  # Esto convierte las filas en diccionarios

    cur.close()

    return result
