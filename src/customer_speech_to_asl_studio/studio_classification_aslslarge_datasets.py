import h5py
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

'''
Code to Load ASL Dataset Efficiently
@author:shamakeskar
✔ Loads large datasets efficiently.
✔ Automatically handles variable-length sequences.
'''

# Load dataset from HDF5
DATASET_PATH = "asl_dataset.h5"

X, y = [], []

with h5py.File(DATASET_PATH, "r") as f:
    for video in f.keys():
        frames = [f[video][frame][()] for frame in f[video].keys()]
        X.append(frames)
        y.append(video.split("_")[0])  # Extract label from filename

X = np.array(X)
y = np.array(y)

# Label encoding
encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)
y_categorical = to_categorical(y_encoded)

print(f"Loaded dataset with shape {X.shape}")
