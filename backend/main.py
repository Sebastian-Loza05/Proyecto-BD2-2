from indice_invertido import preprocess_text, score_tf

def main(textQuery, topK):
    tokens = preprocess_text(textQuery)
    print(tokens)
    query_frecuency = {}
    for i in tokens.split(' '):
        if i not in query_frecuency:
            query_frecuency[i] = 1
        else:
            query_frecuency[i] += 1
    for term, tf in query_frecuency.items():
        query_frecuency[term] = score_tf(tf)

    print(query_frecuency)


query = input("Ingresa la query: ")
topK = int(input("Ingresa el topK: "))

main(query, topK)
