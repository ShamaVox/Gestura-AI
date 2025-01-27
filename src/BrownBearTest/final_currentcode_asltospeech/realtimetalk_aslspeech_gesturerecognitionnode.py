import tensorflow as tf
import mediapipe as mp
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from gtts import gTTS
import os
from collections import deque

# Define gestures
gestures = ["yes", "no", "thanks", "sorry", "please"]
label_encoder = LabelEncoder()
label_encoder.fit(gestures)

# Constants
FEATURE_COUNT = 63  # Number of features per frame
CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence to accept a prediction
BUFFER_SIZE = 15  # Stabilization buffer size
STABILIZATION_THRESHOLD = 0.6  # Majority vote threshold

# Buffers for stabilization
prediction_buffer = deque(maxlen=BUFFER_SIZE)

# Load the trained model
model = tf.keras.models.load_model("/Users/shamakeskar/Desktop/final_gesture_model.h5")

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Gesture labels
gesture_labels = label_encoder.inverse_transform(range(len(gestures)))

def capture_landmarks(frame, hands, mp_drawing):
    """Capture hand landmarks and draw them on the frame."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        landmarks = []
        for lm in results.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp.solutions.hands.HAND_CONNECTIONS)
        return np.array(landmarks[:FEATURE_COUNT]), frame  # Ensure correct feature count
    return None, frame

def stabilize_predictions(buffer):
    """Return the most common prediction if its frequency is above the threshold."""
    if len(buffer) < BUFFER_SIZE:
        return "Detecting..."
    prediction_counts = {gesture: buffer.count(gesture) for gesture in set(buffer)}
    most_common = max(prediction_counts, key=prediction_counts.get)
    confidence = prediction_counts[most_common] / BUFFER_SIZE
    return most_common if confidence >= STABILIZATION_THRESHOLD else "Uncertain"

def speak_text(text):
    """Convert text to speech using gTTS."""
    try:
        tts = gTTS(text=text, lang="en")
        tts.save("gesture.mp3")
        os.system("afplay gesture.mp3")  # Use 'mpg123 gesture.mp3' on Linux or 'start gesture.mp3' on Windows
    except Exception as e:
        print(f"Error in TTS: {e}")

# Webcam setup
cap = cv2.VideoCapture(0)
print("Webcam initialized. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    landmarks, frame = capture_landmarks(frame, hands, mp_drawing)

    if landmarks is not None:
        # Normalize landmarks
        landmarks = np.expand_dims(landmarks, axis=0)  # Shape: (1, FEATURE_COUNT)

        # Predict gesture
        predictions = model.predict(landmarks, verbose=0)
        gesture_index = np.argmax(predictions)
        gesture_confidence = predictions[0][gesture_index]
        gesture_name = gesture_labels[gesture_index]

        # Add prediction to buffer
        if gesture_confidence > CONFIDENCE_THRESHOLD:
            prediction_buffer.append(gesture_name)
        else:
            prediction_buffer.append("Uncertain")

        # Stabilize predictions
        stable_prediction = stabilize_predictions(prediction_buffer)
        if stable_prediction != "Uncertain":
            cv2.putText(frame, f"{stable_prediction}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            speak_text(stable_prediction)
        else:
            cv2.putText(frame, "Detecting...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    else:
        cv2.putText(frame, "No landmarks detected.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Real-Time Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
