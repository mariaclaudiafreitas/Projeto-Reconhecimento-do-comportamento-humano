import mysql.connector
from sklearn.metrics import confusion_matrix
import numpy as np

# Função para conectar ao banco de dados
def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",    # Host do seu banco de dados
        port=3306,            # Porta do MySQL
        user="root",         # Usuário do banco de dados
        password="Art_@2002", # Senha do banco de dados
        database="emocao"  # Nome do banco de dados
    )

# Função para criar a tabela confusion_matrix se não existir
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
    conn.commit()  # Comita as mudanças
    cursor.close()

# Função para inserir dados na tabela confusion_matrix
def inserir_confusion_matrix(conn, classe, classe_prevista, contagem):
    cursor = conn.cursor()
    query = """
        INSERT INTO confusion_matrix (classe, classe_prevista, contagem)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE contagem = contagem + VALUES(contagem);
    """
    cursor.execute(query, (classe, classe_prevista, contagem))
    conn.commit()  # Comita as mudanças
    cursor.close()

# Exemplo de dados: rótulos reais e previstos
y_true = ["happy", "sad", "happy", "angry"]
y_pred = ["happy", "happy", "sad", "angry"]

# Calcular a matriz de confusão
cm = confusion_matrix(y_true, y_pred, labels=["happy", "sad", "angry"])

# Conectar ao banco de dados
conn = conectar()
criar_tabela_confusion_matrix(conn)

# Inserir dados da matriz de confusão na tabela confusion_matrix
for i, classe in enumerate(["happy", "sad", "angry"]):
    for j, classe_prevista in enumerate(["happy", "sad", "angry"]):
        contagem = cm[i][j]
        inserir_confusion_matrix(conn, classe, classe_prevista, contagem)

# Fechar a conexão com o banco de dados
conn.close()
print("Dados da matriz de confusão inseridos com sucesso na tabela 'confusion_matrix'!")
