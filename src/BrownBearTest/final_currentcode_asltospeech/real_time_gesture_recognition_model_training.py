import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
import mediapipe as mp
import cv2
import os

# Dataset Paths
dataset_dir = "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset"
gestures = ["yes", "no", "thanks", "sorry", "please"]

# Load and Preprocess Dataset
def load_dataset(dataset_dir, gestures):
    X = []
    y = []
    for gesture in gestures:
        filepath = os.path.join(dataset_dir, f"{gesture}.npy")
        if os.path.exists(filepath):
            data = np.load(filepath)
            X.append(data)
            y.extend([gesture] * data.shape[0])
    X = np.vstack(X)
    y = np.array(y)
    return X, y

# Load dataset
X, y = load_dataset(dataset_dir, gestures)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Normalize data
X_train = X_train / np.max(X_train)
X_test = X_test / np.max(X_test)

# Model Definition
model = Sequential([
    Dense(256, activation='relu', input_shape=(63,)),
    Dropout(0.4),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(len(gestures), activation='softmax')
])

# Compile Model
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Callbacks
checkpoint_path = "best_gesture_model.h5"
callbacks = [
    ModelCheckpoint(checkpoint_path, save_best_only=True, monitor="val_loss", mode="min"),
    EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
]

# Train Model
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=30,
    batch_size=32,
    callbacks=callbacks
)

# Save Final Model
model.save("/Users/shamakeskar/conferease/src/BrownBearTest/final_gesture_model.h5")
print("Model training complete and saved as 'final_gesture_model.h5'.")

# Evaluate Model
val_loss, val_accuracy = model.evaluate(X_test, y_test)
print(f"Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")
