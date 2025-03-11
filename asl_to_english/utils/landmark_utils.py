import cv2
import os
import numpy as np
import mediapipe as mp
from utils.mediapipe_utils import mediapipe_detection
import h5py
import time


def landmark_to_array(mp_landmark_list):
    """Return a np array of size (nb_keypoints x 3)"""
    keypoints = []
    for landmark in mp_landmark_list.landmark:
        keypoints.append([landmark.x, landmark.y, landmark.z])
    return np.nan_to_num(keypoints)


def extract_landmarks(results):
    """Extract the results of both hands and convert them to a np array of size
    if a hand doesn't appear, return an array of zeros

    :param results: mediapipe object that contains the 3D position of all keypoints
    :return: Two np arrays of size (1, 21 * 3) = (1, nb_keypoints * nb_coordinates) corresponding to both hands
    """
    pose = landmark_to_array(results.pose_landmarks).reshape(99).tolist()

    left_hand = np.zeros(63).tolist()
    if results.left_hand_landmarks:
        left_hand = landmark_to_array(results.left_hand_landmarks).reshape(63).tolist()

    right_hand = np.zeros(63).tolist()
    if results.right_hand_landmarks:
        right_hand = (
            landmark_to_array(results.right_hand_landmarks).reshape(63).tolist()
        )
    return pose, left_hand, right_hand


def save_landmarks_from_video(video_name, hdf5_path='data/dataset/landmarks.hdf5'):
    """
    Extract landmarks from a video and save to an HDF5 file
    
    :param video_name: Name of the video to process
    :param hdf5_path: Path to the HDF5 file to store landmarks
    """
    sign_name = video_name.split("-")[0]
    
    # Prepare landmark arrays
    pose_landmarks = []
    left_hand_landmarks = []
    right_hand_landmarks = []

    # Set the Video stream
    cap = cv2.VideoCapture(
        os.path.join("data", "videos", sign_name, video_name + ".mp4")
    )
    
    with mp.solutions.holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Make detections
                image, results = mediapipe_detection(frame, holistic)

                # Store results
                pose, left_hand, right_hand = extract_landmarks(results)
                pose_landmarks.append(pose)
                left_hand_landmarks.append(left_hand)
                right_hand_landmarks.append(right_hand)
            else:
                break
        cap.release()

    # Convert to numpy arrays
    pose_landmarks = np.array(pose_landmarks)
    left_hand_landmarks = np.array(left_hand_landmarks)
    right_hand_landmarks = np.array(right_hand_landmarks)

    # Open HDF5 file with append mode
    with h5py.File(hdf5_path, 'a') as f:
        # Create a group for this video
        video_group = f.create_group(video_name)
        
        # Create datasets for each landmark type
        video_group.create_dataset('pose', data=pose_landmarks, 
                                   compression='gzip', 
                                   chunks=True)
        video_group.create_dataset('left_hand', data=left_hand_landmarks, 
                                   compression='gzip', 
                                   chunks=True)
        video_group.create_dataset('right_hand', data=right_hand_landmarks, 
                                   compression='gzip', 
                                   chunks=True)
        
        # Add metadata
        video_group.attrs['sign_name'] = sign_name
        video_group.attrs['video_name'] = video_name
        video_group.attrs['timestamp'] = time.time()
        video_group.attrs['num_frames'] = len(pose_landmarks)


def load_landmarks_from_hdf5(video_name, hdf5_path='data/dataset/landmarks.hdf5'):
    """
    Load landmarks for a specific video from HDF5 file
    
    :param video_name: Name of the video to load
    :param hdf5_path: Path to the HDF5 file
    :return: Dictionary of landmarks
    """
    with h5py.File(hdf5_path, 'r') as f:
        video_group = f[video_name]
        return {
            'pose': video_group['pose'][:],
            'left_hand': video_group['left_hand'][:],
            'right_hand': video_group['right_hand'][:]
        }
