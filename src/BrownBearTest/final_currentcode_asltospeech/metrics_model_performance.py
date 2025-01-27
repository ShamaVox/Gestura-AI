import os
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from keras.utils import to_categorical

# Gesture dataset file paths
gesture_files = {
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
    "thank_you": "/Users/shamakeskar/conferease/src/BrownBearTest/demo_augmented_dataset/thank you_augmented.npy",
}

# Load dataset
X = []
y = []

for label, file_path in gesture_files.items():
    try:
        data = np.load(file_path, allow_pickle=True)
        if isinstance(data, list):
            data = np.array(data)
        if len(data) == 0:
            print(f"Skipping {label}: Empty data.")
            continue
        X.append(data)
        y.extend([label] * len(data))
        print(f"Loaded {label}: {data.shape[0]} samples.")
    except Exception as e:
        print(f"Error loading {label}: {e}")

# Ensure consistency
if X:
    X = np.vstack(X)
    y = np.array(y)

    if len(X) != len(y):
        print(f"Inconsistent data sizes: X={len(X)}, y={len(y)}. Please verify dataset integrity.")
    else:
        # Encode labels
        from sklearn.preprocessing import LabelEncoder
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)

        # Split into train and test
        X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

        # One-hot encode labels
        y_train_categorical = to_categorical(y_train, num_classes=len(label_encoder.classes_))
        y_test_categorical = to_categorical(y_test, num_classes=len(label_encoder.classes_))

        # Load model
        model_path = "/Users/shamakeskar/conferease/src/BrownBearTest/demofinal_final_gesture_model_with_face_hands_body.h5"
        model = tf.keras.models.load_model(model_path)

        # Compile model if not already compiled
        model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

        # Evaluate the model
        print("Evaluating the model...")
        metrics = model.evaluate(X_test, y_test_categorical, verbose=1)
        print(f"Test Loss: {metrics[0]}, Test Accuracy: {metrics[1]}")

        # Generate predictions
        y_pred_probs = model.predict(X_test)
        y_pred = np.argmax(y_pred_probs, axis=1)

        # Classification report
        print("Classification Report:")
        print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

        # Overall accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Overall Test Accuracy: {accuracy:.2f}")
else:
    print("No valid data loaded. Please check your .npy files.")
