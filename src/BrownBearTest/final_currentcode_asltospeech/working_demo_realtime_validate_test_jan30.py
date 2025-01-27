import tensorflow as tf
import mediapipe as mp
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from collections import deque
from gtts import gTTS
import os
import playsound

# Define gestures
gestures = [
    "we", "review", "emergency", "process", "attention", "passengers",
    "flight", "newyork", "gate", "proceed", "boarding", "thank you"
]
label_encoder = LabelEncoder()
label_encoder.fit(gestures)

# Constants
EXPECTED_FEATURE_COUNT = 1635  # Match model input shape
BUFFER_SIZE = 10  # Frames for prediction stabilization
CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence for a recognized gesture
DRAW_EVERY = 5  # Frequency for drawing landmarks (every 5 frames)

# Prediction buffer for stabilization
prediction_buffer = deque(maxlen=BUFFER_SIZE)

# Track last spoken gesture
last_spoken = None

def speak(text):
    """Convert text to speech and play it."""
    global last_spoken
    if text != last_spoken:  # Avoid repetitive announcements
        try:
            tts = gTTS(text=text, lang='en')
            filename = "temp_tts.mp3"
            tts.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
            last_spoken = text
        except Exception as e:
            print(f"Error in TTS: {e}")

def preprocess_landmarks(landmarks, expected_shape):
    """Ensure landmarks match the expected shape for the model."""
    if landmarks is None:
        return np.zeros(expected_shape)  # Return zeros if no landmarks detected
    landmarks = landmarks.flatten()
    if len(landmarks) > expected_shape:
        return landmarks[:expected_shape]  # Trim to expected shape
    elif len(landmarks) < expected_shape:
        return np.pad(landmarks, (0, expected_shape - len(landmarks)))  # Pad to expected shape
    return landmarks

def capture_landmarks(frame, hands, face_mesh, mp_drawing, mp_hands, mp_face_mesh):
    """Capture both hand and face landmarks."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_hands = hands.process(frame_rgb)
    results_face = face_mesh.process(frame_rgb)

    hand_landmarks = []
    face_landmarks = []

    # Capture hand landmarks
    if results_hands.multi_hand_landmarks:
        for hand_landmarks_set in results_hands.multi_hand_landmarks:
            for lm in hand_landmarks_set.landmark:
                hand_landmarks.extend([lm.x, lm.y, lm.z])
            mp_drawing.draw_landmarks(frame, hand_landmarks_set, mp_hands.HAND_CONNECTIONS)

    # Capture face landmarks
    if results_face.multi_face_landmarks:
        for face_landmarks_set in results_face.multi_face_landmarks:
            for lm in face_landmarks_set.landmark:
                face_landmarks.extend([lm.x, lm.y, lm.z])
            mp_drawing.draw_landmarks(frame, face_landmarks_set, mp_face_mesh.FACEMESH_CONTOURS)

    combined_landmarks = hand_landmarks + face_landmarks
    return np.array(combined_landmarks) if combined_landmarks else None, frame

# Load trained model
model = tf.keras.models.load_model("/Users/shamakeskar/conferease/src/BrownBearTest/demofinal_final_gesture_model_with_face_hands_body.h5")

# Initialize MediaPipe components
mp_hands = mp.solutions.hands
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

gesture_labels = label_encoder.inverse_transform(range(len(gestures)))

# Webcam setup
cap = cv2.VideoCapture(0)
print("Webcam initialized. Press 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    landmarks, frame = capture_landmarks(frame, hands, face_mesh, mp_drawing, mp_hands, mp_face_mesh)

    if landmarks is not None:
        landmarks = preprocess_landmarks(landmarks, EXPECTED_FEATURE_COUNT)
        landmarks = np.expand_dims(landmarks, axis=0)

        # Model prediction
        predictions = model.predict(landmarks, verbose=0)
        gesture_index = np.argmax(predictions)
        gesture_confidence = predictions[0][gesture_index]

        if gesture_index < len(gesture_labels):  # Ensure valid gesture index
            gesture_name = gesture_labels[gesture_index]

            if gesture_confidence > CONFIDENCE_THRESHOLD:
                prediction_buffer.append(gesture_name)
            else:
                prediction_buffer.append("Uncertain")

            # Majority vote for stabilization
            if len(prediction_buffer) == BUFFER_SIZE:
                stable_prediction = max(set(prediction_buffer), key=prediction_buffer.count)
                cv2.putText(frame, f"{stable_prediction} ({gesture_confidence:.2f})", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                speak(stable_prediction)
            else:
                cv2.putText(frame, "Detecting...", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        else:
            cv2.putText(frame, "Unknown gesture", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            print(f"Invalid gesture index: {gesture_index}")
    else:
        cv2.putText(frame, "No landmarks detected.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Real-Time Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
face_mesh.close()
