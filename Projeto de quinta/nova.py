import cv2
from deepface import DeepFace
from collections import Counter, deque
import paho.mqtt.client as mqtt
import json

# Configurações do broker MQTT
MQTT_BROKER = "localhost"  # Endereço do broker MQTT (localhost ou remoto)
MQTT_PORT = 1883            # Porta padrão para conexão MQTT
#MQTT_TOPIC = "emotion_data" # tópico onde você deseja publicar a mensagem

# Função chamada quando uma mensagem é recebida
def on_message(cliente, userdata, msg):
    # Exibe a mensagem recebida no console
    print(f"Received PUBLISH from {client._client_id.decode()} (d0, q0, r0, m0, '{msg.topic}', ... '{msg.payload.decode()}')")

# Criar um cliente MQTT
client = mqtt.Client()       # Inicializa um novo cliente MQTT

# Conectar-se ao broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT)  # Conecta ao broker utilizando as configurações especificadas

# Função de moda ponderada
def moda_ponderada(valores, pesos):
    # Contar as ocorrências das emoções detectadas
    contagem = Counter(valores)  
    soma_ponderada = {}  # Dicionário para armazenar a soma ponderada das emoções

    # Calcular a soma ponderada para cada emoção
    for i, valor in enumerate(valores):
        soma_ponderada[valor] = soma_ponderada.get(valor, 0) + pesos[i]  # Adiciona o peso correspondente à emoção

    # Encontrar a emoção com a maior soma ponderada
    moda = max(soma_ponderada, key=soma_ponderada.get)
    return moda  # Retorna a emoção predominante

# Carregar o classificador de faces
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')# Carrega o classificador Haar para detecção de rostos

# Ligar a câmera
cap = cv2.VideoCapture(0)  # Inicializa a captura de vídeo da câmera padrão

# Cores para cada pessoa
cores = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Define cores para retângulos ao redor das faces (vermelho, verde, azul)

# Lista para armazenar as últimas 3 emoções
historico_emocoes = deque(maxlen=3)  # Inicializa uma fila para armazenar as emoções detectadas (máximo de 3)

# Loop principal
while True:
    ret, frame = cap.read()  # Captura um quadro da câmera

    if not ret:
        print("Falha ao capturar imagem da câmera.")
        break  # Encerra o loop se a captura falhar

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Converte o quadro para escala de cinza
    
    # Detecta faces na imagem em escala de cinza
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    dominant_emotions = []  # Lista para armazenar emoções dominantes detectadas
    emotion_weights = []    # Lista para armazenar os pesos das emoçõe

    # Loop através das faces detectadas
    for i, (x, y, w, h) in enumerate(faces):
        roi_color = frame[y:y+h, x:x+w]  # Extrai a região da face do quadro
        
        # Analisa a região da face para determinar a emoção
        results = DeepFace.analyze(roi_color, actions=['emotion'], enforce_detection=False)

        if isinstance(results, list):
            result = results[0]  # Se o resultado for uma lista, pega o primeiro elemento
        else:
            result = results
        
        dominant_emotion = result['dominant_emotion']  # Obtém a emoção predominante
        dominant_emotions.append(dominant_emotion)  # Adiciona a emoção à lista
        
        emotion_confidence = result['emotion'][dominant_emotion]  # Obtém o nível de confiança da emoção
        emotion_weights.append(emotion_confidence)  # Adiciona o peso da emoção à lista
        
        cor = cores[i % len(cores)]  # Seleciona a cor para desenhar o retângulo em volta da face
        
        cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)  # Desenha um retângulo ao redor da face detectada

    # Se houver emoções dominantes detectadas
    if dominant_emotions:
        historico_emocoes.extend(dominant_emotions)  # Adiciona emoções ao histórico
        
        if len(historico_emocoes) == 3:  # Se o histórico tiver 3 emoções
            pesos = [1] * len(historico_emocoes)  # Define pesos iguais para todas as emoções
            emotion_moda = moda_ponderada(historico_emocoes, pesos)  # Calcula a emoção predominante
            # Exibe a emoção predominante geral na imagem
            cv2.putText(frame, f"Emocao predominante geral: {emotion_moda}", (3, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Exibe emoções detectadas para cada pessoa
    for i, dominant_emotion in enumerate(dominant_emotions):
        cor = cores[i % len(cores)]  # Seleciona a cor para desenhar o texto
        # Desenha texto com a emoção dominante para cada pessoa
        cv2.putText(frame, f"Pessoa {i+1}: {dominant_emotion}", (10, 100 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
        
        # Se a emoção dominante for "happy", publica uma mensagem no broker MQTT
        if dominant_emotion == "happy":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "happy"
            
        # Se a emoção dominante for "suprise", publica uma mensagem no broker MQTT
        if dominant_emotion == "surprise":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada   
            # Publicar a mensagem no tópico correspondente à emoção
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "surprise"
            
        # Se a emoção dominante for "sad", publica uma mensagem no broker MQTT
        if dominant_emotion == "sad":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada  
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "sad"
            
        # Se a emoção dominante for "fear", publica uma mensagem no broker MQTT
        if dominant_emotion == "fear":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada   
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "fear"
            
        # Se a emoção dominante for "neutral", publica uma mensagem no broker MQTT
        if dominant_emotion == "neutral":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "neutral"
            
        # Se a emoção dominante for "angry", publica uma mensagem no broker MQTT
        if dominant_emotion == "angry":
            message = f"A pessoa está {dominant_emotion}"  # Mensagem a ser publicada   
            client.publish(dominant_emotion, message)  # Publica a mensagem no tópico "angry"
            
    
    # Exibe o quadro com as emoções e faces detectadas
    cv2.imshow("Detector de emoções", frame)
    
    # Aguarda uma tecla pressionada por 150 milissegundos, se a tecla 'q' for pressionada, encerra o loop
    if cv2.waitKey(150) & 0xFF == ord('q'):
        break
    
# Fechar a conexão MQTT
client.disconnect()  # Desconecta do broker MQTT

# Fechar todas as janelas e liberar a câmera
cv2.destroyAllWindows()  # Fecha todas as janelas abertas
cap.release()  # Libera o objeto de captura da câmera

print("Encerrou")  # Imprime mensagem de encerramento do programa
