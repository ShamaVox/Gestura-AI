import tensorflow as tf
import mediapipe as mp
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder
from gtts import gTTS
import os
import playsound
import time

# @author:shamavox
# working demo script = to be used same model to create customer sales demo

# Define gestures in strict order
gestures = [
    "we", "review", "emergency", "process", "attention", "passengers",
    "flight", "newyork", "gate", "proceed", "boarding", "thank you"
]
label_encoder = LabelEncoder()
label_encoder.fit(gestures)

# Constants
EXPECTED_FEATURE_COUNT = 1635  # Match model input shape
CONFIDENCE_THRESHOLD = 0.8  # Minimum confidence for recognized gesture
FRAME_LIMIT_PER_GESTURE = 150  # Max frames to wait for the current gesture
ANNOUNCEMENT_DELAY = 1.5  # Seconds to delay between detection and announcement

# Track current gesture index and frame counter
current_gesture_index = 0
frame_counter = 0

def speak(text):
    """Convert text to speech and play it."""
    try:
        tts = gTTS(text=text, lang='en')
        filename = "temp_tts.mp3"
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
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

        # Check if the recognized gesture matches the current one in the sequence
        if gesture_index == current_gesture_index and gesture_confidence > CONFIDENCE_THRESHOLD:
            cv2.putText(frame, f"Recognized: {gestures[current_gesture_index]} ({gesture_confidence:.2f})", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            time.sleep(ANNOUNCEMENT_DELAY)  # Add delay before announcing
            speak(gestures[current_gesture_index])
            current_gesture_index = (current_gesture_index + 1) % len(gestures)  # Move to the next gesture
            frame_counter = 0  # Reset frame counter
        else:
            cv2.putText(frame, f"Detecting: {gestures[current_gesture_index]}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    else:
        cv2.putText(frame, f"Waiting for gesture: {gestures[current_gesture_index]}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    frame_counter += 1
    if frame_counter >= FRAME_LIMIT_PER_GESTURE:
        # Move to the next gesture after a timeout
        time.sleep(ANNOUNCEMENT_DELAY)  # Add delay before announcing
        speak(f"Recognized: {gestures[current_gesture_index]}")
        current_gesture_index = (current_gesture_index + 1) % len(gestures)
        frame_counter = 0  # Reset frame counter

    cv2.imshow("Real-Time Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
face_mesh.close()
