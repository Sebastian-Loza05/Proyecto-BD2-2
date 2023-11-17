import psycopg2
import time

conn = psycopg2.connect(
    host="localhost",
    database="BD2Proyecto2",
    user="postgres",
    port = 5432,
    password="utec"
)

cur = conn.cursor()

def search(Q, k):
    query = Q.split(" ")
    query = '|'.join(query)
    top_k = k

    start = time.time()

    cur.execute(f"""
        SELECT track_artist, track_name, ts_rank_cd(full_text, query, 1) AS rank
        FROM songslist, to_tsquery('english', '{query}') query
        WHERE query @@ full_text
        ORDER BY rank DESC
        LIMIT {top_k};
    """)

    end = time.time()

    result = cur.fetchall()
    conn.commit()
    conn.close()


    for row in result:
        print(row)

    print("Tiempo de ejecucion :",
          (end - start) * 10 ** 3, "ms")

search("Justin Biber", 100)
