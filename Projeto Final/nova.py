# nova.py
import cv2
from deepface import DeepFace
from collections import Counter, deque
import paho.mqtt.client as mqtt
import mysql.connector
from emocao import gerar_matriz_confusao  # Importa a função para criar matriz de confusão

# Configurações MQTT e MySQL
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT)

def conectar_banco():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="Art_@2002",
        database="emocao"
    )
    return conn

def inserir_emocao(conn, usuario_id, emocao, contagem):
    cursor = conn.cursor()
    query = "INSERT INTO emocao_contagem (usuario_id, emocao, contagem) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (usuario_id, emocao, contagem))
    conn.commit()
    cursor.close()

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
conn = conectar_banco()

frames_por_usuario = 10
historico_emocoes_por_usuario = {}
usuario_id = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Falha ao capturar imagem da câmera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    
    for (x, y, w, h) in faces:
        roi_color = frame[y:y+h, x:x+w]
        results = DeepFace.analyze(roi_color, actions=['emotion'], enforce_detection=False)
        dominant_emotion = results[0]['dominant_emotion']
        
        # Identifique e incremente as emoções de cada usuário
        if usuario_id not in historico_emocoes_por_usuario:
            historico_emocoes_por_usuario[usuario_id] = deque(maxlen=frames_por_usuario)
        
        historico_emocoes_por_usuario[usuario_id].append(dominant_emotion)

        if len(historico_emocoes_por_usuario[usuario_id]) == frames_por_usuario:
            emotion_counts = Counter(historico_emocoes_por_usuario[usuario_id])
            for emocao, contagem in emotion_counts.items():
                inserir_emocao(conn, usuario_id, emocao, contagem)
                client.publish("emocao/usuario", f"Usuário {usuario_id} - Emoção {emocao}: {contagem}")
            
            # Gerar matriz de confusão e salvar no banco
            gerar_matriz_confusao(historico_emocoes_por_usuario[usuario_id], conn, usuario_id)
            del historico_emocoes_por_usuario[usuario_id]  # Reset para o próximo usuário
            usuario_id += 1

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"Emoção: {dominant_emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Detector de emoções", frame)

    if cv2.waitKey(150) & 0xFF == ord('q'):
        break

client.disconnect()
conn.close()
cap.release()
cv2.destroyAllWindows()
