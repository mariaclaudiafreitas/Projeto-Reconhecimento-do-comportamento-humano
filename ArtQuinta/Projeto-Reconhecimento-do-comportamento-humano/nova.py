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
        database="emocao"    # Nome do banco de dados
    )
    return conn

# Função para inserir a contagem de emoções no banco de dados
def inserir_emocao(conn, emocao, contagem):
    cursor = conn.cursor()
    query = "INSERT INTO emocao_contagem (emocao, contagem) VALUES (%s, %s)"
    cursor.execute(query, (emocao, contagem))
    conn.commit()
    cursor.close()

# Carregar o classificador de faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Ligar a câmera
cap = cv2.VideoCapture(0)

# Cores para cada pessoa
cores = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

# Lista para armazenar as últimas 3 emoções
historico_emocoes = deque(maxlen=3)

# Inicializa a conexão com o banco de dados
conn = conectar_banco()

# Loop principal
while True:
    ret, frame = cap.read()
    if not ret:
        print("Falha ao capturar imagem da câmera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    print(f"Faces detectadas: {len(faces)}")  # Adiciona uma verificação

    dominant_emotions = []
    emotion_weights = []

    for i, (x, y, w, h) in enumerate(faces):
        roi_color = frame[y:y+h, x:x+w]
        results = DeepFace.analyze(roi_color, actions=['emotion'], enforce_detection=False)

        if isinstance(results, list):
            result = results[0]
        else:
            result = results

        dominant_emotion = result['dominant_emotion']
        dominant_emotions.append(dominant_emotion)
        emotion_confidence = result['emotion'][dominant_emotion]
        emotion_weights.append(emotion_confidence)

        cor = cores[i % len(cores)]
        cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)

    if dominant_emotions:
        historico_emocoes.extend(dominant_emotions)

        if len(historico_emocoes) == 3:
            pesos = [1] * len(historico_emocoes)
            emotion_moda = moda_ponderada(historico_emocoes, pesos)

            # Exibe a emoção predominante geral na imagem
            cv2.putText(frame, f"Emocao predominante geral: {emotion_moda}", (3, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Contar a ocorrência da emoção predominante
            count = dominant_emotions.count(emotion_moda)
            # Inserir no banco de dados
            inserir_emocao(conn, emotion_moda, count)

    # Exibe emoções detectadas para cada pessoa
    for i, dominant_emotion in enumerate(dominant_emotions):
        cor = cores[i % len(cores)]
        cv2.putText(frame, f"Pessoa {i+1}: {dominant_emotion}", (10, 100 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

        # Publicar mensagem no MQTT
        client.publish(dominant_emotion, f"A pessoa está {dominant_emotion}")

    cv2.imshow("Detector de emoções", frame)
    
    if cv2.waitKey(150) & 0xFF == ord('q'):
        break

# Fechar a conexão MQTT e com o banco de dados
client.disconnect()
conn.close()  # Fecha a conexão com o banco de dados

# Fechar todas as janelas e liberar a câmera
cv2.destroyAllWindows()
cap.release()

print("Encerrou")  # imprime a mensagem de encerramento
