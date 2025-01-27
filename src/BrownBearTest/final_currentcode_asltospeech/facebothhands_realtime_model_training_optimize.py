import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Dataset paths
file_paths = {
    "we": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augumented_dataset/we.npy",
    "review": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/review.npy",
    "emergency": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/emergency.npy",
    "process": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/process.npy"
}

# Load and preprocess the dataset
X = []  # Features
y = []  # Labels

max_length = 0  # To calculate the maximum feature length

for gesture, path in file_paths.items():
    try:
        # Load data with pickle enabled
        data = np.load(path, allow_pickle=True)

        for sample in data:
            hands_data = sample.get("hands", [])
            face_data = sample.get("face", [])

            # Ensure both are numpy arrays
            hands_data = np.array(hands_data).flatten() if hands_data else np.zeros(63)
            face_data = np.array(face_data).flatten() if face_data else np.zeros(1404)

            # Concatenate features
            combined_features = np.concatenate([hands_data, face_data])
            max_length = max(max_length, len(combined_features))  # Track max length
            X.append(combined_features)
            y.append(gesture)

    except Exception as e:
        print(f"Error with gesture {gesture}: {e}")

# Pad features to the maximum length
X_padded = []
for features in X:
    if len(features) < max_length:
        # Pad with zeros
        padded = np.pad(features, (0, max_length - len(features)), 'constant')
        X_padded.append(padded)
    else:
        X_padded.append(features)

# Convert lists to numpy arrays
X = np.array(X_padded)
y = np.array(y)

# Encode labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Split dataset into training and validation
X_train, X_val, y_train, y_val = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Normalize features
X_train = X_train / np.max(X_train, axis=1, keepdims=True)
X_val = X_val / np.max(X_val, axis=1, keepdims=True)

# Define the model
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
    ModelCheckpoint("best_gesture_model_with_face_hands.h5", save_best_only=True, monitor='val_loss', mode='min')
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
model.save("/Users/shamakeskar/conferease/src/BrownBearTest/final_gesture_model_with_face_hands.h5")

# Evaluate the model
val_loss, val_accuracy = model.evaluate(X_val, y_val)
print(f"Validation Loss: {val_loss:.4f}, Validation Accuracy: {val_accuracy:.4f}")

# Classification Report
y_pred = np.argmax(model.predict(X_val), axis=1)
from sklearn.metrics import classification_report
print("\nClassification Report:")
print(classification_report(y_val, y_pred, target_names=label_encoder.classes_))
