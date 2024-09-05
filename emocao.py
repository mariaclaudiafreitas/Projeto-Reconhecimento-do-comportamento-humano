import cv2
from deepface import DeepFace

# Iniciando a captura de vídeo
webcam = cv2.VideoCapture(0)

# Carregando o classificador Haar para detecção de faces
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

try:
    while True:
        ret, frame = webcam.read()
        if not ret:
            break
        
        # Convertendo para escala de cinza para melhor detecção de face
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectando faces na imagem
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            # Recortando o rosto para análise
            face_roi = frame[y:y+h, x:x+w]
            
            # Analisando a emoção do rosto
            try:
                results = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                if isinstance(results, list):
                    result = results[0]  # Caso o resultado seja uma lista, pegar o primeiro elemento
                else:
                    result = results
                
                dominant_emotion = result['dominant_emotion']
                
                # Definindo a cor da bounding box com base na emoção detectada
                if dominant_emotion == 'angry':
                    box_color = (0, 0, 255)  # Vermelho para raiva
                else:
                    box_color = (255, 0, 0)  # Azul para outras emoções
                
                # Desenhando a bounding box em volta do rosto
                cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)
                
                # Exibindo a emoção dominante na bounding box
                cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, box_color, 2)
            except Exception as e:
                print("Erro ao analisar o frame:", e)
        
        # Mostrando a imagem com a bounding box e a emoção detectada
        cv2.imshow("Emotion Detection", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    webcam.release()
    cv2.destroyAllWindows()