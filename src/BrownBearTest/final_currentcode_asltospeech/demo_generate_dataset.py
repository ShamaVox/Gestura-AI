import cv2
import mediapipe as mp
import numpy as np
import os
import time
import json

# @author:shamavox
# working demo script = to be used same model to create customer sales demo

# MediaPipe Hands and Face setup
mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_mesh
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
)
face_mesh = mp_face.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
)
mp_drawing = mp.solutions.drawing_utils

# Output directory
output_dataset_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/demo_airport_gesture_dataset"
gestures = ["attention", "passengers", "flight", "newyork", "boarding", "gate 7", "please", "proceed", "thank you"]
os.makedirs(output_dataset_dir, exist_ok=True)

# Webcam setup
print("Initializing webcam...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Unable to access the webcam.")
    exit()

print("Webcam initialized. Press Enter to save a sample, 'q' to quit.")

def capture_landmarks(frame):
    """Capture landmarks from hands and face."""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results_hands = hands.process(frame_rgb)
    results_face = face_mesh.process(frame_rgb)

    hands_landmarks = []
    face_landmarks = []

    if results_hands.multi_hand_landmarks:
        for hand_landmarks in results_hands.multi_hand_landmarks:
            hand_data = []
            for lm in hand_landmarks.landmark:
                hand_data.extend([lm.x, lm.y, lm.z])
            hands_landmarks.append(hand_data)
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    if results_face.multi_face_landmarks:
        for face_landmarks_set in results_face.multi_face_landmarks:
            face_data = []
            for lm in face_landmarks_set.landmark:
                face_data.extend([lm.x, lm.y, lm.z])
            face_landmarks.append(face_data)
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks_set,
                mp_face.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1, circle_radius=1),
            )

    return {"hands": hands_landmarks, "face": face_landmarks}, frame

# Loop through gestures
for gesture in gestures:
    print(f"\nRecording gesture: '{gesture}'. Starting in 5 seconds...")
    time.sleep(5)
    print("Recording started. Press Enter to save a sample, 'q' to quit.")

    data = []
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame. Exiting...")
            break

        frame = cv2.flip(frame, 1)
        landmarks, frame = capture_landmarks(frame)

        if landmarks["hands"] or landmarks["face"]:
            cv2.putText(frame, "Landmarks detected!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hands or face detected.", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow("ASL Dataset Collection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 13:  # Enter key
            if landmarks["hands"] or landmarks["face"]:
                data.append(landmarks)
                print(f"Saved a sample for '{gesture}'. Total samples: {len(data)}")
        elif key == ord("q"):
            print(f"Finished recording for '{gesture}'.")
            break

    if len(data) < 1:
        print(f"Insufficient samples for '{gesture}'. Recorded: {len(data)}. Skipping.")
        continue

    # Save the gesture data
    output_path = os.path.join(output_dataset_dir, f"{gesture}.npy")
    np.save(output_path, np.array(data, dtype=object))
    print(f"Dataset saved for '{gesture}' with {len(data)} samples.")

cap.release()
cv2.destroyAllWindows()
hands.close()
face_mesh.close()
print("Dataset generation complete.")
