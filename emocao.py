# emocao.py
import time
import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)  # Certifique-se de que a câmera está disponível

# Função para monitorar e contar emoções
def monitorar_emocoes(period=30):
    # Dicionário para contar as emoções
    emotion_count = {"happy": 0, "sad": 0, "angry": 0, "surprise": 0, "fear": 0, "neutral": 0 }
    
    # Lista para armazenar o histórico de emoções e horários
    emotion_history = []

    start_time = time.time()

    # Loop infinito para monitorar emoções
    while True:
        ret, frame = cap.read()  # Captura o frame da câmera
        if not ret:
            break

        # Analisa a emoção do frame
        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)

        # Armazena a emoção com o timestamp
        current_time = time.time()
        dominant_emotion = result['dominant_emotion']  # Modificado para acessar corretamente o resultado
        
        # Adiciona ao histórico
        emotion_history.append((dominant_emotion, current_time))
        
        # Atualiza a contagem
        emotion_count[dominant_emotion] += 1

        # Remove emoções fora do intervalo de tempo
        emotion_history = [(emotion, timestamp) for emotion, timestamp in emotion_history if current_time - timestamp <= period]

        # Exibe a contagem atual
        print(f"Emoções nas últimas {period} segundos: {emotion_count}")
        
        # Intervalo de 1 segundo entre cada verificação
        time.sleep(1)

    cap.release()  # Libera a câmera quando o loop termina
    return emotion_count  # Retorna a contagem de emoções
