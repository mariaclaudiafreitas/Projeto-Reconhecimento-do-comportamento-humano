import cv2
from deepface import DeepFace
from collections import Counter

# Load Haar Cascade
haarcascade_path = "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(haarcascade_path)

# Start video capture
cap = cv2.VideoCapture(0)

# Counter to track emotions
emotion_counter = Counter()

print("Press 'q' to quit.")

while True:
    # Read video frame
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale for detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Extract and preprocess face
        face_roi = frame[y:y+h, x:x+w]

        try:
            if face_roi.size > 0:
                # Resize face to 224x224 for DeepFace
                face_roi = cv2.resize(face_roi, (224, 224))
                
                # Analyze emotion
                emotion = DeepFace.analyze(face_roi, actions=['emotion'], enforce_detection=False)
                print("DeepFace output:", emotion)  # Debugging: Inspect the output
                
                # Handle both list and dictionary outputs
                if isinstance(emotion, list):
                    # Extract dominant emotion from the first dictionary in the list
                    emotion_label = emotion[0].get('dominant_emotion', 'Unknown')
                elif isinstance(emotion, dict):
                    # Extract dominant emotion directly from the dictionary
                    emotion_label = emotion.get('dominant_emotion', 'Unknown')
                else:
                    emotion_label = "Invalid output"

                # Update emotion counter
                emotion_counter[emotion_label] += 1
            else:
                emotion_label = "Invalid face"
        except Exception as e:
            # Capture errors
            emotion_label = "Error"
            print(f"Error analyzing face at ({x}, {y}): {str(e)}")

        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Display emotion or error message
        cv2.putText(frame, emotion_label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Show the video frame
    cv2.imshow("Emotion Detection", frame)

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Print emotion statistics as a table
print("\nEmotion Detection Summary:")
print("-" * 30)
print(f"{'Emotion':<15}{'Count':<10}")
print("-" * 30)
for emotion in ['happy', 'sad', 'angry', 'surprise', 'fear', 'neutral']:
    print(f"{emotion:<15}{emotion_counter.get(emotion, 0):<10}")
print("-" * 30)
