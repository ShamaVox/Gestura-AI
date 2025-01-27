
import tensorflow as tf
import mediapipe as mp
import numpy as np
import cv2
from sklearn.preprocessing import LabelEncoder

gestures = ["yes", "no", "thanks", "sorry", "please"]
label_encoder = LabelEncoder()
label_encoder.fit(gestures)

# Real-Time Gesture Recognition
def capture_landmarks(frame, hands, mp_drawing):
    """Extract hand landmarks from a frame using MediaPipe."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        landmarks = []
        for lm in results.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp.solutions.hands.HAND_CONNECTIONS)
        return np.array(landmarks), frame
    return None, frame

# Load trained model
model = tf.keras.models.load_model("/Users/shamakeskar/conferease/src/BrownBearTest/final_gesture_model.h5")

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Gesture labels
gesture_labels = label_encoder.inverse_transform(range(len(gestures)))

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
        # Preprocess landmarks
        landmarks = np.expand_dims(landmarks, axis=0)
        landmarks = landmarks / np.max(landmarks)

        # Predict gesture
        predictions = model.predict(landmarks)
        gesture_index = np.argmax(predictions)
        gesture_confidence = predictions[0][gesture_index]
        gesture_name = gesture_labels[gesture_index]

        if gesture_confidence > 0.7:  # Confidence threshold
            cv2.putText(frame, f"{gesture_name} ({gesture_confidence:.2f})", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "Uncertain Gesture", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Real-Time Gesture Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
