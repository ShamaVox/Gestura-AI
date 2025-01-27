import numpy as np
import os
import random

# @author:shamavox
# automated samples == dataset creation however original dataset needs to be symmetrical
# working demo script = to be used same model to create customer sales demo
# Paths to the original .npy files for each gesture
input_files = {
    
   
    "gate": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_airport_gesture_dataset/gate 7.npy",
    "please": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_airport_gesture_dataset/please.npy",
    "proceed": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_airport_gesture_dataset/proceed.npy",
    "thank you": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_airport_gesture_dataset/thank you.npy"
}

# Path to save augmented files
output_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/1demo_augmented_dataset"
os.makedirs(output_dir, exist_ok=True)

# Number of augmented samples to generate per gesture
target_samples = 500

# Augmentation functions
def add_noise(data, noise_level=0.01):
    """Add random noise to landmarks."""
    data = np.array(data)  # Ensure input is a NumPy array
    noise = np.random.normal(0, noise_level, data.shape)
    return data + noise

def scale_landmarks(data, scale_factor=0.95):
    """Scale landmarks slightly."""
    data = np.array(data)  # Ensure input is a NumPy array
    return data * scale_factor

def rotate_landmarks(data, angle=5):
    """Rotate landmarks by a small angle."""
    data = np.array(data)  # Ensure input is a NumPy array
    angle_rad = np.radians(angle)
    rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                 [np.sin(angle_rad), np.cos(angle_rad)]])
    rotated = []
    for hand in data:
        hand = np.array(hand)  # Ensure each hand is an array
        if hand.ndim == 1:  # If 1D, reshape to 2D
            hand = hand.reshape(-1, 3)  # Assuming (x, y, z) format
        if hand.shape[1] >= 2:  # Ensure we have x and y columns
            xy = np.stack([hand[:, 0], hand[:, 1]], axis=-1)
            rotated_xy = np.dot(xy, rotation_matrix.T)
            hand[:, 0] = rotated_xy[:, 0]
            hand[:, 1] = rotated_xy[:, 1]
        rotated.append(hand)
    return np.array(rotated)

def mirror_landmarks(data):
    """Mirror landmarks along the x-axis."""
    data = np.array(data)  # Ensure input is a NumPy array
    mirrored = data.copy()
    mirrored[..., 0] = -mirrored[..., 0]  # Flip x-coordinates
    return mirrored

def translate_landmarks(data, shift=0.02):
    """Translate landmarks by a small amount."""
    data = np.array(data)  # Ensure input is a NumPy array
    translation = np.random.uniform(-shift, shift, size=data.shape)
    return data + translation

def augment_body(body_landmarks):
    """Apply augmentation to body landmarks."""
    body_landmarks = np.array(body_landmarks)  # Ensure input is a NumPy array
    if np.random.rand() > 0.5:
        body_landmarks = add_noise(body_landmarks, noise_level=0.01)
    if np.random.rand() > 0.5:
        body_landmarks = scale_landmarks(body_landmarks, scale_factor=1.02)
    if np.random.rand() > 0.5:
        body_landmarks = translate_landmarks(body_landmarks, shift=0.03)
    return body_landmarks

def augment_face(face_landmarks):
    """Apply augmentation to face landmarks."""
    face_landmarks = np.array(face_landmarks)  # Ensure input is a NumPy array
    if np.random.rand() > 0.5:
        face_landmarks = add_noise(face_landmarks, noise_level=0.02)
    if np.random.rand() > 0.5:
        face_landmarks = scale_landmarks(face_landmarks, scale_factor=1.02)
    if np.random.rand() > 0.5:
        face_landmarks = rotate_landmarks([face_landmarks], angle=random.randint(-5, 5))[0]
    return face_landmarks

def augment_hands(hands_landmarks):
    """Apply augmentation to hand landmarks."""
    augmented_hands = []
    for hand in hands_landmarks:
        hand = np.array(hand)  # Ensure input is a NumPy array
        if hand.ndim == 1:  # Handle 1D arrays
            hand = hand.reshape(-1, 3)  # Assuming (x, y, z) format
        if np.random.rand() > 0.5:
            hand = add_noise(hand, noise_level=0.02)
        if np.random.rand() > 0.5:
            hand = scale_landmarks(hand, scale_factor=1.03)
        if np.random.rand() > 0.5:
            hand = rotate_landmarks([hand], angle=np.random.randint(-10, 10))[0]
        if np.random.rand() > 0.5:
            hand = mirror_landmarks(hand)
        if np.random.rand() > 0.5:
            hand = translate_landmarks(hand, shift=0.02)
        augmented_hands.append(hand)
    return augmented_hands

# Process each gesture file
for gesture_name, input_file in input_files.items():
    print(f"Processing gesture: {gesture_name}")

    # Load the original landmarks data
    original_data = np.load(input_file, allow_pickle=True)

    # Generate augmented data
    augmented_data = []
    for _ in range(target_samples):
        for sample in original_data:
            augmented_sample = sample.copy()

            # Augment hands
            if "hands" in augmented_sample and augmented_sample["hands"]:
                augmented_sample["hands"] = augment_hands(augmented_sample["hands"])

            # Augment face
            if "face" in augmented_sample and augmented_sample["face"]:
                augmented_sample["face"] = augment_face(augmented_sample["face"])

            # Augment body (if available)
            if "body" in augmented_sample and augmented_sample["body"]:
                augmented_sample["body"] = augment_body(augmented_sample["body"])

            augmented_data.append(augmented_sample)

            # Stop if target samples are reached
            if len(augmented_data) >= target_samples:
                break

    # Save the augmented data
    output_file = os.path.join(output_dir, f"{gesture_name}_augmented.npy")
    np.save(output_file, np.array(augmented_data[:target_samples], dtype=object))
    print(f"Augmented dataset saved for '{gesture_name}' to {output_file} with {len(augmented_data[:target_samples])} samples.")
