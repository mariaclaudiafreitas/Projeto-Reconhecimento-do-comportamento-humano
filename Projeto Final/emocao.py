# emocao.py
import numpy as np
import pandas as pd
from collections import Counter

def gerar_matriz_confusao(emocoes, conn, usuario_id):
    emotions_list = ["happy", "sad", "angry", "surprise", "fear", "neutral"]
    counts = Counter(emocoes)
    
    matriz = np.zeros((len(emotions_list), len(emotions_list)), dtype=int)
    
    for emotion, count in counts.items():
        row = emotions_list.index(emotion)
        matriz[row][row] = count

    df = pd.DataFrame(matriz, index=emotions_list, columns=emotions_list)
    cursor = conn.cursor()
    for emocao, contagem in counts.items():
        query = "INSERT INTO matriz_confu (usuario_id, emocao, contagem) VALUES (%s, %s, %s)"
        cursor.execute(query, (usuario_id, emocao, contagem))
    conn.commit()
    cursor.close()
    
    return df
