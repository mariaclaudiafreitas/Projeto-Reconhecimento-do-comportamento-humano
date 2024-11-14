import mysql.connector

# Função para conectar ao banco de dados
def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Art_@2002",
        database="emocao"
    )

# Função para inserir dados na tabela confusion_matrix
def inserir_confusion_matrix(emocao, happy, sad, neutral,fear,angry,surprise):
    conn = conectar()
    cursor = conn.cursor()
    
    # Insere os valores de emoção e porcentagem na tabela confusion_matrix
    query = "INSERT INTO confusion_matrix (emocao, happy, sad, neutral, fear, angry, surprise) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (emocao, happy, sad, neutral, fear, angry, surprise))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função para registrar a contagem de uma emoção no banco de dados
def inserir_emocao_contagem(emocao, contagem):
    conn = conectar()
    cursor = conn.cursor()
    
    # Insere a emoção e a contagem na tabela emocao_contagem
    query = "INSERT INTO emocao_contagem (emocao, contagem) VALUES (%s, %s)"
    cursor.execute(query, (emocao, contagem))
    
    conn.commit()
    cursor.close()
    conn.close()

# Exemplo de inserção de dados para testes
if __name__ == "__main__":
    # Exemplo de matriz de confusão
    inserir_confusion_matrix('happy', 80.0, 15.0, 5.0)
    inserir_confusion_matrix('sad', 10.0, 85.0, 5.0)
    inserir_confusion_matrix('neutral', 5.0, 10.0, 85.0)
    
    # Exemplo de contagem de emoções
    inserir_emocao_contagem('happy', 5)
    inserir_emocao_contagem('sad', 3)
    inserir_emocao_contagem('neutral', 7)

    print("Dados inseridos com sucesso.")
