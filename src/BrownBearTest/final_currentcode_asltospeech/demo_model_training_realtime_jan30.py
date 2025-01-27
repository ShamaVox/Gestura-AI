import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report
import os

# @author:shamavox
# working demo script = to be used same model to create customer sales demo

# Dataset paths
file_paths = {
    "we": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/we_augmented.npy",
    "review": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/review_augmented.npy",
    "emergency": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/emergency_augmented.npy",
    "process": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/process_augmented.npy",
    "attention": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/attention_augmented.npy",
    "passengers": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/passengers_augmented.npy",
    "flight": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/flight_augmented.npy",
    "newyork": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/newyork_augmented.npy",
    "boarding": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/boarding_augmented.npy",
    "gate": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/gate_augmented.npy",
    "please": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/please_augmented.npy",
    "proceed": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/proceed_augmented.npy",
    "thank_you": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/thank you_augmented.npy"
}

# Ensure all files exist
for gesture, path in file_paths.items():
    if not os.path.exists(path):
        print(f"Error: File for gesture '{gesture}' not found at {path}. Please ensure all files are present.")
        exit(1)

# Initialize variables
X = []  # Features
y = []  # Labels
max_length = 0  # Track maximum feature length for padding

# Load and preprocess the dataset
for gesture, path in file_paths.items():
    print(f"Processing gesture: {gesture}")
    try:
        data = np.load(path, allow_pickle=True)[:500]  # Limit to 500 samples per gesture

        for sample in data:
            hands_data = sample.get("hands", [])
            face_data = sample.get("face", [])
            body_data = sample.get("body", [])

            # Ensure data is numpy arrays
            hands_data = np.array(hands_data).flatten() if len(hands_data) > 0 else np.zeros(63)
            face_data = np.array(face_data).flatten() if len(face_data) > 0 else np.zeros(1404)
            body_data = np.array(body_data).flatten() if len(body_data) > 0 else np.zeros(75)

            # Combine features
            combined_features = np.concatenate([hands_data, face_data, body_data])
            max_length = max(max_length, len(combined_features))  # Update max length
            X.append(combined_features)
            y.append(gesture)
    except Exception as e:
        print(f"Error processing {gesture}: {e}")
        exit(1)

# Pad features to maximum length
X_padded = []
for features in X:
    padded = np.pad(features, (0, max_length - len(features)), 'constant')
    X_padded.append(padded)

# Convert lists to numpy arrays
X = np.array(X_padded)
y = np.array(y)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split the dataset into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Normalize features
X_train = X_train / np.max(X_train, axis=1, keepdims=True)
X_val = X_val / np.max(X_val, axis=1, keepdims=True)

# Build the model
model = Sequential([
    Dense(512, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.4),
    Dense(256, activation='relu'),
    Dropout(0.3),
    Dense(128, activation='relu'),
    Dropout(0.2),
    Dense(len(label_encoder.classes_), activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Define callbacks
callbacks = [
    EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
    ModelCheckpoint("/Users/shamakeskar/conferease/src/BrownBearTest/demofinal_best_gesture_model_with_face_hands_body.h5", 
                    save_best_only=True, monitor='val_loss', mode='min')
]

# Train the model
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    batch_size=32,
    callbacks=callbacks
)

# Save the final model
model.save("/Users/shamakeskar/conferease/src/BrownBearTest/demofinal_final_gesture_model_with_face_hands_body.h5")

# Evaluate the model
val_loss, val_accuracy = model.evaluate(X_val, y_val)
print(f"Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")

# Generate classification report
y_pred = np.argmax(model.predict(X_val), axis=1)
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=label_encoder.classes_))
