import numpy as np
import os

# Paths to existing and new datasets
dataset_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset"
new_dataset_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_new_dataset"
gestures = ["yes", "no", "thanks", "sorry", "please"]

# Merge datasets
for gesture in gestures:
    existing_path = os.path.join(dataset_dir, f"{gesture}.npy")
    new_path = os.path.join(new_dataset_dir, f"{gesture}.npy")

    if os.path.exists(existing_path) and os.path.exists(new_path):
        # Load existing and new data
        existing_data = np.load(existing_path)
        new_data = np.load(new_path)

        # Merge data
        combined_data = np.vstack([existing_data, new_data])

        # Save combined dataset
        np.save(existing_path, combined_data)
        print
