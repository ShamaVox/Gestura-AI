import cv2
import mediapipe as mp
import numpy as np
import json
from scipy.spatial.transform import Rotation as R

def numpy_to_list(obj):
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: numpy_to_list(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [numpy_to_list(item) for item in obj]
    return obj

def calculate_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def add_t_pose(animation_data):
    # Get the first frame's data
    first_frame = animation_data["keyframes"][0]["landmarks"]["pose"]
    
    # Calculate lengths and distances
    shoulder_width = calculate_distance(first_frame['left_shoulder'], first_frame['right_shoulder'])
    upper_arm_length = calculate_distance(first_frame['left_shoulder'], first_frame['left_elbow'])
    forearm_length = calculate_distance(first_frame['left_elbow'], first_frame['left_wrist'])
    torso_length = calculate_distance(first_frame['left_shoulder'], first_frame['left_hip'])
    hip_width = calculate_distance(first_frame['left_hip'], first_frame['right_hip'])
    
    # Create T-pose using the head position as anchor
    head_pos = np.array(first_frame['head'])
    t_pose = {
        'head': head_pos.tolist(),
        'left_shoulder': (head_pos + [-shoulder_width/2, 0, -torso_length/4]).tolist(),
        'right_shoulder': (head_pos + [shoulder_width/2, 0, -torso_length/4]).tolist(),
        'left_elbow': (head_pos + [-shoulder_width/2 - upper_arm_length, 0, -torso_length/4]).tolist(),
        'right_elbow': (head_pos + [shoulder_width/2 + upper_arm_length, 0, -torso_length/4]).tolist(),
        'left_wrist': (head_pos + [-shoulder_width/2 - upper_arm_length - forearm_length, 0, -torso_length/4]).tolist(),
        'right_wrist': (head_pos + [shoulder_width/2 + upper_arm_length + forearm_length, 0, -torso_length/4]).tolist(),
        'left_hip': (head_pos + [-hip_width/2, 0, -torso_length]).tolist(),
        'right_hip': (head_pos + [hip_width/2, 0, -torso_length]).tolist()
    }
    
    t_pose_frame = {
        "frame": 0,
        "landmarks": {"pose": t_pose}
    }
    
    # Insert T-pose as the first frame
    animation_data["keyframes"].insert(0, t_pose_frame)
    
    # Adjust frame numbers for subsequent keyframes
    for i in range(1, len(animation_data["keyframes"])):
        animation_data["keyframes"][i]["frame"] += 1
    
    return animation_data

def calculate_rotation(parent, child, initial_direction):
    direction = np.array(child) - np.array(parent)
    rotation = R.align_vectors([direction], [initial_direction])[0]
    return rotation.as_euler('XYZ', degrees=True)

def calculate_rotations(frame_data):
    rotations = {}
    
    # Define initial directions (in T-pose)
    initial_directions = {
        'Head': [0, 0, 1],
        'Shoulder.L': [-1, 0, 0],
        'Shoulder.R': [1, 0, 0],
        'Elbow.L': [-1, 0, 0],
        'Elbow.R': [1, 0, 0],
        'Wrist.L': [-1, 0, 0],
        'Wrist.R': [1, 0, 0],
        'Hip.L': [0, 0, -1],
        'Hip.R': [0, 0, -1]
    }
    
    # Calculate rotations for each bone
    rotations['Head'] = calculate_rotation(frame_data['left_shoulder'], frame_data['head'], initial_directions['Head'])
    rotations['Shoulder.L'] = calculate_rotation(frame_data['left_shoulder'], frame_data['left_elbow'], initial_directions['Shoulder.L'])
    rotations['Shoulder.R'] = calculate_rotation(frame_data['right_shoulder'], frame_data['right_elbow'], initial_directions['Shoulder.R'])
    rotations['Elbow.L'] = calculate_rotation(frame_data['left_elbow'], frame_data['left_wrist'], initial_directions['Elbow.L'])
    rotations['Elbow.R'] = calculate_rotation(frame_data['right_elbow'], frame_data['right_wrist'], initial_directions['Elbow.R'])
    
    # For hips, we'll use the direction from the opposite shoulder to the hip
    rotations['Hip.L'] = calculate_rotation(frame_data['right_shoulder'], frame_data['left_hip'], initial_directions['Hip.L'])
    rotations['Hip.R'] = calculate_rotation(frame_data['left_shoulder'], frame_data['right_hip'], initial_directions['Hip.R'])
    
    return rotations

def normalize_coordinates(animation_data):
    all_coords_list = []
    for frame in animation_data['keyframes']:
        for landmark, coords in frame['landmarks']['pose'].items():
            all_coords_list.append(coords)

    all_coords = np.array(all_coords_list)    
    max_coords = np.max(all_coords, axis=0)
    min_coords = np.min(all_coords, axis=0)
    
    # Normalize to range [-1, 1] and convert to Blender coordinate system
    normalized_data = animation_data.copy()
    for frame in normalized_data['keyframes']:
        for landmark, coords in frame['landmarks']['pose'].items():
            normalized_coords = [
                2 * (coords[0] - min_coords[0]) / (max_coords[0] - min_coords[0]) - 1,  # X (left/right)
                2 * (coords[2] - min_coords[2]) / (max_coords[2] - min_coords[2]) - 1,  # Y (front/back)
                2 * (coords[1] - min_coords[1]) / (max_coords[1] - min_coords[1]) - 1   # Z (top/bottom)
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

    normalized_animation_data = add_t_pose(normalized_animation_data)

    for frame in normalized_animation_data['keyframes']:
        frame['rotations'] = calculate_rotations(frame['landmarks']['pose'])
    
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
    serializable_data = numpy_to_list(animation_data)
    with open(output_file, 'w') as f:
        json.dump(serializable_data, f, indent=2)

if __name__ == '__main__':
    video_path = 'WLASL/start_kit/raw_videos/05727.mp4'
    animation_data = process_video(video_path, num_frames=80)
    save_animation_data(animation_data, 'animation_data.json')