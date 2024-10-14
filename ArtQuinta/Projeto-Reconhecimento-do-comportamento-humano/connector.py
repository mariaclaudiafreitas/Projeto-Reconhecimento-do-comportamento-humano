import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Art_@2002",
        database="emocao"
    )

# Função para inserir dados na tabela confusion_matrix
def inserir_confusion_matrix(emocao, happy, sad, neutral):
    conn = conectar()
    cursor = conn.cursor()
    
    # Insere os valores de emoção e porcentagem na tabela confusion_matrix
    query = "INSERT INTO confusion_matrix (emocao, happy, sad, neutral) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (emocao, happy, sad, neutral))
    
    conn.commit()
    cursor.close()
    conn.close()

# Exemplo de inserção de dados
if __name__ == "__main__":
    inserir_confusion_matrix('happy', 80.0, 15.0, 5.0)
    inserir_confusion_matrix('sad', 10.0, 85.0, 5.0)
    inserir_confusion_matrix('neutral', 5.0, 10.0, 85.0)

    print("Dados inseridos com sucesso.")
