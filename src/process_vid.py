import cv2
import mediapipe as mp
import numpy as np
import json

def normalize_coordinates(animation_data):
    all_coords_list = []
    for frame in animation_data['keyframes']:
        for landmark, coords in frame['landmarks']['pose'].items():
            all_coords_list.append(coords)

    all_coords = np.array(all_coords_list)    
    max_x = np.max(all_coords[:, 0])
    min_x = np.min(all_coords[:, 0])
    max_y = np.max(all_coords[:, 1])
    min_y = np.min(all_coords[:, 1])
    max_z = np.max(all_coords[:, 2])
    min_z = np.min(all_coords[:, 2])
    
    max_coords = [max_x, max_y, max_z]
    min_coords = [min_x, min_y, min_z]
    
    # Normalize to range [0, 1]
    normalized_data = animation_data.copy()
    for frame in normalized_data['keyframes']:
        for landmark, coords in frame['landmarks']['pose'].items():
            normalized_coords = [
                (coords[i] - min_coords[i]) / (max_coords[i] - min_coords[i])
                for i in range(3)  # For x, y, z
            ]
            frame['landmarks']['pose'][landmark] = normalized_coords
    
    return normalized_data

def convert_to_3d(landmark, image_width, image_height, scale_factor=1):
    x = (1 - landmark.x) * image_width * scale_factor  # Invert X
    y = (1 - landmark.y) * image_height * scale_factor  # Invert Y
    z = landmark.z * scale_factor
    return [x, y, z]

def process_frame_holistic(frame, mp_holistic, image_width, image_height):
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = mp_holistic.process(image)
    
    frame_data = {}
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        pose_data = {
            'left_shoulder': convert_to_3d(landmarks[11], image_width, image_height),
            'right_shoulder': convert_to_3d(landmarks[12], image_width, image_height),
            'left_elbow': convert_to_3d(landmarks[13], image_width, image_height),
            'right_elbow': convert_to_3d(landmarks[14], image_width, image_height),
            'left_wrist': convert_to_3d(landmarks[15], image_width, image_height),
            'right_wrist': convert_to_3d(landmarks[16], image_width, image_height),
        }
        
        # Calculate average Z-value of shoulders
        avg_shoulder_z = (pose_data['left_shoulder'][2] + pose_data['right_shoulder'][2]) / 2
        
        # Set head and hips with adjusted Z-value
        pose_data['head'] = convert_to_3d(landmarks[0], image_width, image_height)
        pose_data['head'][2] = avg_shoulder_z
        
        pose_data['left_hip'] = convert_to_3d(landmarks[23], image_width, image_height)
        pose_data['left_hip'][2] = avg_shoulder_z
        
        pose_data['right_hip'] = convert_to_3d(landmarks[24], image_width, image_height)
        pose_data['right_hip'][2] = avg_shoulder_z
        
        frame_data['pose'] = pose_data
    
    return frame_data

def process_video(video_path, num_frames=80):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frame_indices = np.linspace(0, frame_count - 1, num_frames, dtype=int)

    animation_data = {
        "frame_rate": fps,
        "keyframes": []
    }
    
    mp_holistic = mp.solutions.holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    all_coords = {'x': [], 'y': [], 'z': []}
    
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if not ret:
            print(f"Failed to read frame {frame_index}")
            continue
        
        frame_data = process_frame_holistic(frame, mp_holistic, frame_width, frame_height)

        if 'pose' in frame_data:
            for landmark in frame_data['pose'].values():
                all_coords['x'].append(landmark[0])
                all_coords['y'].append(landmark[1])
                all_coords['z'].append(landmark[2])
                    
        animation_data["keyframes"].append({
            "frame": int(frame_index),
            "landmarks": frame_data
        })

    cap.release()
    
    # Normalize the coordinates
    normalized_animation_data = normalize_coordinates(animation_data)
    
    # Calculate bounds of normalized data
    all_coords = np.array([
        [coord for landmark in frame['landmarks']['pose'].values() for coord in landmark]
        for frame in normalized_animation_data['keyframes']
    ])
    
    normalized_animation_data['bounds'] = {
        'x': [np.min(all_coords[:, 0]), np.max(all_coords[:, 0])],
        'y': [np.min(all_coords[:, 1]), np.max(all_coords[:, 1])],
        'z': [np.min(all_coords[:, 2]), np.max(all_coords[:, 2])]
    }
    
    return normalized_animation_data

def save_animation_data(animation_data, output_file):
    with open(output_file, 'w') as f:
        json.dump(animation_data, f, indent=2)

if __name__ == '__main__':
    video_path = 'WLASL/start_kit/raw_videos/05727.mp4'
    animation_data = process_video(video_path, num_frames=80)
    save_animation_data(animation_data, 'animation_data.json')