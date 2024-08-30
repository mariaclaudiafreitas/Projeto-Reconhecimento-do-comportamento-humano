from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import LabelEncoder
import numpy as np
import cv2
import sys

# Carregar o conjunto de dados FER2013
train_dir = 'image/train'
validation_dir = 'image/validation'

train_datagen = ImageDataGenerator(rescale=1./255)
validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(train_dir, target_size=(48, 48), batch_size=32, class_mode='categorical')
validation_generator = validation_datagen.flow_from_directory(validation_dir, target_size=(48, 48), batch_size=32, class_mode='categorical')

# Criar o modelo de reconhecimento de emoção
model = Sequential()
model.add(Input(shape=(48, 48, 3)))
model.add(Conv2D(32, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(128, activation='relu'))
model.add(Dense(5, activation='softmax'))

# Compilar o modelo
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Treinar o modelo
history = model.fit(train_generator, epochs=10, validation_data = validation_generator)

# Salvar o modelo treinado
model.save('emotion_model.h5')

# Carregar o modelo de detecção de rosto
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Carregar o modelo de reconhecimento de emoção
emotion_model = load_model('emotion_model.h5')

# Capturar o vídeo da câmera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detectar o rosto
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Extrair características faciais
    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        # Redimensionar a imagem para o tamanho do modelo de reconhecimento de emoção
        roi_gray = cv2.resize(roi_gray, (48, 48))
        
        # Normalizar a imagem
        roi_gray = roi_gray / 255.0
        
        # Expandir as dimensões para o modelo de reconhecimento de emoção
        roi_gray = np.expand_dims(roi_gray, axis=0)
        
        # Fazer a previsão da emoção
        emotion_prediction = emotion_model.predict(roi_gray)
        
        # Obter a emoção com a probabilidade mais alta
        emotion = np.argmax(emotion_prediction)
        
        # Imprimir a emoção no terminal
        print("Emoção:", ["Neutro", "Feliz", "Triste", "Surpreso", "Raivoso"][emotion], file=sys.stdout.buffer, encoding='utf-8')
        
    cv2.imshow("Versao1", frame)
    cv2.waitKey(1)

    if cv2.getWindowProperty("Versao1", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
cap.release()
print("Encerrou")