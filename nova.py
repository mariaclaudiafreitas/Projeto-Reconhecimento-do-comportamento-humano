# importando as bibliotecas
import cv2
from deepface import DeepFace

# carregar um arquivo especial que nos ajuda a detectar rostos em imagens
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# ligar a câmera
cap = cv2.VideoCapture(0)

# este loop continuará lendo frames da câmera e analisando-os
while True:
    # ler um único quadro da câmera. ret é a variavel que diz se o quadro foi lido corrtamente e frame é a variavel que armazena a imagem real
    ret, frame = cap.read()
    
    # convertendo a imagem colorida para uma imagem em tons de cinza (preto e branco)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # usando o blueprint de detecção de faces para encontrar todas as faces na imagem em tons de cinza. A detectMultiScalefunção retorna uma lista de todas as faces que encontrou
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # iniciando um loop que passará por cada face que encontrar
    for (x, y, w, h) in faces:
        
        # extraindo a região do rosto da imagem colorida original
        roi_color = frame[y:y+h, x:x+w]
        
        # usando a ferramenta DeepFace para analisar a região do rosto e descobrir qual emoção a pessoa está sentindo
        results = DeepFace.analyze(roi_color, actions=['emotion'], enforce_detection=False)
        
        # verificando se o resultado é uma lista
        if isinstance(results, list):
            
            # caso o resultado seja uma lista, pegar o primeiro elemento
            result = results[0] 
        else:
            # se o resultado não for uma lista, usaremos apenas o resultado único
            result = results
        
        # extraindo a emoção dominante do resultado
        dominant_emotion = result['dominant_emotion']
        
    # desenhando um rótulo de texto na imagem original com a emoção dominante
    cv2.putText(frame, dominant_emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 4)
    
    # exibindo a imagem com o rótulo de texto
    cv2.imshow("Detector de emocoes", frame)
    
    # esperando um curto período de tempo (1 milissegundo) antes de ler o próximo quadro
    cv2.waitKey(1)

    # verificando se a janela ainda está aberta ai se apertar o X vai fechar a aba
    if cv2.getWindowProperty("Detector de emocoes", cv2.WND_PROP_VISIBLE) < 1:
        break

# fechando todas as janelas
cv2.destroyAllWindows()

# liberando a câmera
cap.release()

# imprimindo uma mensagem para dizer que o programa terminou
print("Encerrou")