import cv2
from deepface import DeepFace
from collections import Counter, deque
import paho.mqtt.client as mqtt 
import json


# Configurações do broker MQTT
MQTT_BROKER = "localhost"  # ou o endereço do seu broker remoto
MQTT_PORT = 1883
MQTT_TOPIC = "emotion_data"  # tópico onde você deseja publicar a mensagem

# Criar um cliente MQTT
client = mqtt.Client()

# Conectar-se ao broker MQTT
client.connect(MQTT_BROKER, MQTT_PORT)

# Função de moda ponderada
def moda_ponderada(valores, pesos):
    # Contar as ocorrências dos valores
    contagem = Counter(valores)
    
    # Calcular a soma ponderada das ocorrências
    soma_ponderada = {}
    for i, valor in enumerate(valores):
        soma_ponderada[valor] = soma_ponderada.get(valor, 0) + pesos[i]
    
    # Encontrar o valor com a maior soma ponderada
    moda = max(soma_ponderada, key=soma_ponderada.get)
    
    return moda

# carregar um arquivo especial que nos ajuda a detectar rostos em imagens
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# ligar a câmera
cap = cv2.VideoCapture(0)

# cores para cada pessoa
cores = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # vermelho, verde, azul

# Lista para armazenar as últimas 3 emoções
historico_emocoes = deque(maxlen=3)

# este loop continuará lendo frames da câmera e analisando-os
while True:
    # ler um único quadro da câmera. ret é a variavel que diz se o quadro foi lido corrtamente e frame é a variavel que armazena a imagem real
    ret, frame = cap.read()
    
    if not ret:
        print("Falha ao capturar imagem da câmera.")
        break

    # convertendo a imagem colorida para uma imagem em tons de cinza (preto e branco)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # usando o blueprint de detecção de faces para encontrar todas as faces na imagem em tons de cinza
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # inicializar as emoções dominantes e os pesos como listas vazias
    dominant_emotions = []
    emotion_weights = []

    # iniciando um loop que passará por cada face que encontrar
    for i, (x, y, w, h) in enumerate(faces):
        # extraindo a região do rosto da imagem colorida original
        roi_color = frame[y:y+h, x:x+w]
        
        # usando a ferramenta DeepFace para analisar a região do rosto e descobrir qual emoção a pessoa está sentindo
        results = DeepFace.analyze(roi_color, actions=['emotion'], enforce_detection=False)
        
        # verificando se o resultado é uma lista
        if isinstance(results, list):
            result = results[0]
        else:
            result = results
        
        # extraindo a emoção dominante do resultado
        dominant_emotion = result['dominant_emotion']
        
        # adicionando a emoção dominante à lista
        dominant_emotions.append(dominant_emotion)
        
        # pegando o valor de confiança como peso
        emotion_confidence = result['emotion'][dominant_emotion]
        emotion_weights.append(emotion_confidence)
        
        # escolher a cor para a pessoa atual
        cor = cores[i % len(cores)]  
        
        # desenhando um retângulo ao redor da face com a cor correspondente
        cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)

    # Adicionar emoções detectadas ao histórico
    if dominant_emotions:
        historico_emocoes.extend(dominant_emotions)
        
        # Se houver pelo menos uma emoção no histórico, calcular a moda ponderada
        if len(historico_emocoes) == 3:  # Após 3 capturas, calcular a moda
            pesos = [1] * len(historico_emocoes)  # Peso uniforme para simplificar
            emotion_moda = moda_ponderada(historico_emocoes, pesos)
            
            # desenhar o resultado da moda ponderada na imagem (emoção predominante de todas as pessoas)
            cv2.putText(frame, f"Emocao predominante geral: {emotion_moda}", (3, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # desenhando rótulos de texto na imagem original com as emoções dominantes
    for i, dominant_emotion in enumerate(dominant_emotions):
        # escolher a cor para a pessoa atual
        cor = cores[i % len(cores)] 
        
        # desenhar um texto na imagem frame com a emoção dominante da pessoa
        cv2.putText(frame, f"Pessoa {i+1}: {dominant_emotion}", (10, 100 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
        
        if dominant_emotion == "angry":
            # Criar uma mensagem JSON com a emoção detectada
            message = {"emotion": "angry", "confidence": emotion_confidence}
            message_json = json.dumps(message)

        # Publicar a mensagem no tópico MQTT
        client.publish(MQTT_TOPIC, message_json)
    
    # exibindo a imagem com os rótulos de texto
    cv2.imshow("Detector de emoções", frame)
    
    # esperando um curto período de tempo (150 milissegundo) antes de ler o próximo quadro
    if cv2.waitKey(150) & 0xFF == ord('q'):
        break
    
# Fechar a conexão MQTT
client.disconnect()

# fechando todas as janelas
cv2.destroyAllWindows()

# liberando a câmera
cap.release()

# imprimindo uma mensagem para dizer que o programa terminou
print("Encerrou")
