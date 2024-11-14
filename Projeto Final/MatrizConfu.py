from sklearn.metrics import confusion_matrix
import numpy as np
from connector import conectar  # Importa a função de conexão do banco de dados

# Função para criar a tabela confusion_matrix se ela não existir
def criar_tabela_confusion_matrix(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS confusion_matrix (
            classe VARCHAR(255),
            classe_prevista VARCHAR(255),
            contagem INT,
            PRIMARY KEY (classe, classe_prevista)
        );
    """)
    conn.commit()
    cursor.close()

# Função para inserir ou atualizar dados na tabela confusion_matrix
def inserir_confusion_matrix(conn, classe, classe_prevista, contagem):
    cursor = conn.cursor()
    query = """
        INSERT INTO confusion_matrix (classe, classe_prevista, contagem)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE contagem = contagem + VALUES(contagem);
    """
    cursor.execute(query, (classe, classe_prevista, contagem))
    conn.commit()
    cursor.close()

# Função para calcular e atualizar a matriz de confusão no banco de dados
def atualizar_matriz_confusao(y_true, y_pred, labels):
    # Calcular a matriz de confusão
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    # Conectar ao banco de dados e criar a tabela se necessário
    conn = conectar()
    criar_tabela_confusion_matrix(conn)
    
    # Inserir cada valor da matriz de confusão na tabela
    for i, classe in enumerate(labels):
        for j, classe_prevista in enumerate(labels):
            contagem = cm[i][j]
            if contagem > 0:  # Inserir apenas contagens maiores que zero
                inserir_confusion_matrix(conn, classe, classe_prevista, contagem)
    
    # Fechar a conexão com o banco de dados
    conn.close()
    print("Matriz de confusão atualizada com sucesso na tabela 'confusion_matrix'!")

# Exemplo de uso com rótulos reais e previstos
if __name__ == "__main__":
    y_true = ["happy", "sad", "happy", "angry"]
    y_pred = ["happy", "happy", "sad", "angry"]
    labels = ["happy", "sad", "angry"]
    
    atualizar_matriz_confusao(y_true, y_pred, labels)
