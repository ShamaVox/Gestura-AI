import cv2
import mediapipe as mp
import numpy as np
import os
import time
import json

# MediaPipe Hands setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.7
)
mp_drawing = mp.solutions.drawing_utils

# Output directory
output_dataset_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset"
gestures = ["we", "review", "emergency", "process"]
# gestures = ["yes", "no", "thanks", "sorry", "please"]
os.makedirs(output_dataset_dir, exist_ok=True)

# Webcam setup
print("Initializing webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Unable to access the webcam.")
    exit()

print("Webcam initialized. Press 's' to save landmarks, 'q' to quit.")

def capture_landmarks(frame):
    """Capture landmarks from a frame."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        landmarks = []
        for lm in results.multi_hand_landmarks[0].landmark:
            landmarks.extend([lm.x, lm.y, lm.z])
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
        return np.array(landmarks)
    return None

# Loop through gestures
for gesture in gestures:
    print(f"\nRecording gesture: '{gesture}'. Starting in 5 seconds...")
    time.sleep(5)
    print("Recording started. Press 's' to save a sample, 'q' to finish.")

    data = []
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame. Exiting...")
            break

        frame = cv2.flip(frame, 1)
        landmarks = capture_landmarks(frame)

        if landmarks is not None:
            cv2.putText(frame, "Landmarks detected!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hand detected.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("ASL Dataset Collection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') and landmarks is not None:
            data.append(landmarks)
            print(f"Saved a sample for '{gesture}'. Total samples: {len(data)}")
        elif key == ord('q'):
            print(f"Finished recording for '{gesture}'.")
            break

    # Enforce minimum sample count
    if len(data) < 200:
        print(f"Insufficient samples for '{gesture}'. Recorded: {len(data)}. Skipping.")
        continue

    # Save data
    output_path = os.path.join(output_dataset_dir, f"{gesture}.npy")
    np.save(output_path, np.array(data))
    print(f"Dataset saved for '{gesture}' with {len(data)} samples.")

    # Save metadata
    metadata = {
        "gesture": gesture,
        "timestamp": time.time(),
        "samples": len(data),
        "frame_resolution": (frame.shape[1], frame.shape[0])  # Width, Height
    }
    metadata_path = os.path.join(output_dataset_dir, f"{gesture}_metadata.json")
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

cap.release()
cv2.destroyAllWindows()
hands.close()
print("Dataset generation complete.")
