import cv2
from deepface import DeepFace
from collections import Counter, deque
import paho.mqtt.client as mqtt
import mysql.connector  # Para conectar ao banco de dados

# Configurações do broker MQTT
MQTT_BROKER = "localhost"  # Endereço do broker MQTT (localhost ou remoto)
MQTT_PORT = 1883            # Porta padrão para conexão MQTT

# Criar um cliente MQTT
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

# Função de moda ponderada
def moda_ponderada(valores, pesos):
    soma_ponderada = {}
    for i, valor in enumerate(valores):
        soma_ponderada[valor] = soma_ponderada.get(valor, 0) + pesos[i]
    moda = max(soma_ponderada, key=soma_ponderada.get)
    return moda

# Função para conectar ao banco de dados
def conectar_banco():
    # Configure a conexão com seu banco de dados MySQL
    conn = mysql.connector.connect(
        host="127.0.0.1",    # Host do seu banco de dados
        port=3306,            # Porta do MySQL (opcional, mas bom incluir)
        user="root",         # Usuário do banco de dados
        password="Art_@2002", # Senha do banco de dados
        database="emocao"  # Nome do banco de dados
    )
    return conn

# Função para inserir emoções no banco de dados
def inserir_emocao(emocao, porcentagem):
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Insere a emoção no banco de dados (tabela precisa existir)
    query = "INSERT INTO emocao (emocao, porcentagem) VALUES (%s, %s)"
    cursor.execute(query, (emocao, porcentagem))
    
    conn.commit()
    cursor.close()
    conn.close()

# Função principal para capturar emoções
def capturar_emocao():
    cap = cv2.VideoCapture(0)  # Abre a câmera
    historico_emocoes = deque(maxlen=10)  # Histórico das últimas 10 emoções
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Analisar emoção com o DeepFace
        resultados = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        emocao_dominante = resultados['dominant_emotion']
        porcentagem = resultados['emotion'][emocao_dominante]

        historico_emocoes.append(emocao_dominante)  # Armazena no histórico

        # Calcular a moda do histórico
        moda_emocao = Counter(historico_emocoes).most_common(1)[0][0]

        # Publicar a emoção no broker MQTT
        client.publish("emocao", moda_emocao)

        # Inserir a emoção no banco de dados
        inserir_emocao(moda_emocao, porcentagem)

        # Exibir o resultado na tela
        cv2.putText(frame, f"Emocao: {emocao_dominante} ({porcentagem:.2f}%)", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capturar_emocao()  # Inicia o processo de captura de emoções
