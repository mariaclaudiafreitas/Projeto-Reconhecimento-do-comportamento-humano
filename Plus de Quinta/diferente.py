import cv2
from deepface import DeepFace
from collections import Counter, deque
import paho.mqtt.client as mqtt
import json
import pymysql  # Para conectar ao MySQL
import pyodbc  # Para conectar ao SQL Server

# Configurações do broker MQTT
MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# Função chamada quando uma mensagem é recebida
def on_message(client, userdata, msg):
    print(f"Received PUBLISH from {client._client_id.decode()} (d0, q0, r0, m0, '{msg.topic}', ... '{msg.payload.decode()}')")

# Criar cliente MQTT
client = mqtt.Client()

# Conectar ao broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT)

# Conexão com o banco de dados MySQL
db = pymysql.connect(
    host="localhost",
    user="root",
    password="sua_senha",
    database="nome_do_banco"
)

# Conexão com o SQL Server
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost;'  # Substitua pelo nome do seu servidor
    'DATABASE=nome_do_banco_sql_server;'  # Substitua pelo nome do seu banco de dados SQL Server
    'UID=sa;'  # Substitua pelo nome de usuário do SQL Server
    'PWD=sua_senha;'  # Substitua pela sua senha
)

cursor_sql = conn.cursor()  # Criar cursor para SQL Server

# Criar tabela se não existir no MySQL
cursor_mysql = db.cursor()
cursor_mysql.execute("""
    CREATE TABLE IF NOT EXISTS emocoes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        pessoa VARCHAR(50),
        emocao VARCHAR(50),
        peso FLOAT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Exemplo de consulta no SQL Server
cursor_sql.execute("SELECT * FROM sua_tabela_sql_server")  # Substitua pelo nome da tabela que deseja consultar
for row in cursor_sql:
    print(row)

# Função de moda ponderada
def moda_ponderada(valores, pesos):
    contagem = Counter(valores)
    soma_ponderada = {}
    for i, valor in enumerate(valores):
        soma_ponderada[valor] = soma_ponderada.get(valor, 0) + pesos[i]
    moda = max(soma_ponderada, key=soma_ponderada.get)
    return moda

# Carregar classificador de faces
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Ligar câmera
cap = cv2.VideoCapture(0)

cores = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Definir cores para retângulos ao redor das faces

# Fila para histórico de emoções
historico_emocoes = deque(maxlen=3)

# Emoções relevantes
emoções_relevantes = ['happy', 'surprise', 'fear', 'angry', 'sad']

# Loop principal
while True:
    ret, frame = cap.read()

    if not ret:
        print("Falha ao capturar imagem da câmera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

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
        emotion_confidence = result['emotion'][dominant_emotion]

        # Verificar se a emoção está entre as emoções relevantes
        if dominant_emotion in emoções_relevantes:
            dominant_emotions.append(dominant_emotion)
            emotion_weights.append(emotion_confidence)

            cor = cores[i % len(cores)]
            cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)

            try:
                # Inserir dados no banco de dados MySQL
                cursor_mysql.execute("""
                    INSERT INTO emocoes (pessoa, emocao, peso) VALUES (%s, %s, %s)
                """, (f'Pessoa {i+1}', dominant_emotion, emotion_confidence))
                db.commit()
                print(f"Dados inseridos com sucesso no MySQL: Pessoa {i+1}, Emoção: {dominant_emotion}, Confiança: {emotion_confidence}")

                # Inserir dados no SQL Server (se necessário)
                cursor_sql.execute("""
                    INSERT INTO sua_tabela_sql_server (pessoa, emocao, peso) VALUES (?, ?, ?)
                """, (f'Pessoa {i+1}', dominant_emotion, emotion_confidence))
                conn.commit()
                print(f"Dados inseridos com sucesso no SQL Server: Pessoa {i+1}, Emoção: {dominant_emotion}, Confiança: {emotion_confidence}")

            except Exception as e:
                print(f"Erro ao inserir dados: {e}")

    if dominant_emotions:
        historico_emocoes.extend(dominant_emotions)
        
        if len(historico_emocoes) == 3:
            pesos = [1] * len(historico_emocoes)
            emotion_moda = moda_ponderada(historico_emocoes, pesos)
            cv2.putText(frame, f"Emocao predominante geral: {emotion_moda}", (3, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    for i, dominant_emotion in enumerate(dominant_emotions):
        cor = cores[i % len(cores)]
        cv2.putText(frame, f"Pessoa {i+1}: {dominant_emotion}", (10, 100 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
        
        if dominant_emotion == "happy":
            message = f"A pessoa está {dominant_emotion}"
            client.publish(dominant_emotion, message)

    cv2.imshow("Detector de emoções", frame)
    
    if cv2.waitKey(150) & 0xFF == ord('q'):
        break

# Fechar conexões
db.close()
conn.close()  # Fechar conexão com o SQL Server
client.disconnect()

cv2.destroyAllWindows()
cap.release()

print("Encerrou")
