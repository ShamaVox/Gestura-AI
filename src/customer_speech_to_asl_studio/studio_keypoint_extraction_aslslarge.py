import cv2
import mediapipe as mp
import numpy as np
import os
import h5py
import multiprocessing
from tqdm import tqdm

'''
Code for Faster Keypoint Extraction
@author:shamakeskar
✔ Parallel Processing speeds up extraction.
✔ HDF5 storage for efficient large dataset handling.
✔ Extracts pose, hands, and face keypoints for better ASL recognition.
'''


# Initialize MediaPipe Holistic Model
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Directory for dataset
DATASET_DIR = "asl_videos/"
OUTPUT_FILE = "asl_dataset.h5"

# Function to extract keypoints from a single video
def extract_keypoints(video_file):
    video_path = os.path.join(DATASET_DIR, video_file)
    cap = cv2.VideoCapture(video_path)
    holistic = mp_holistic.Holistic()
    
    frame_data = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(image)

        keypoints = {
            "pose": [[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark] if results.pose_landmarks else [[0, 0, 0]] * 33,
            "hands": [
                [[lm.x, lm.y, lm.z] for lm in results.right_hand_landmarks.landmark] if results.right_hand_landmarks else [[0, 0, 0]] * 21,
                [[lm.x, lm.y, lm.z] for lm in results.left_hand_landmarks.landmark] if results.left_hand_landmarks else [[0, 0, 0]] * 21,
            ],
            "face": [[lm.x, lm.y, lm.z] for lm in results.face_landmarks.landmark] if results.face_landmarks else [[0, 0, 0]] * 468,
        }

        frame_data.append(keypoints)

    cap.release()
    holistic.close()
    return (video_file, frame_data)

# Process dataset in parallel
video_files = os.listdir(DATASET_DIR)
num_workers = multiprocessing.cpu_count()

with multiprocessing.Pool(num_workers) as pool:
    results = list(tqdm(pool.imap(extract_keypoints, video_files), total=len(video_files)))

# Save keypoints to HDF5 (better for large datasets)
with h5py.File(OUTPUT_FILE, "w") as f:
    for video_name, frames in results:
        grp = f.create_group(video_name)
        for i, frame in enumerate(frames):
            grp.create_dataset(f"frame_{i}", data=np.array(frame["pose"] + frame["hands"][0] + frame["hands"][1] + frame["face"]))

print(f"Keypoints extracted and saved in {OUTPUT_FILE}")
