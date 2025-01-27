import numpy as np

# Replace with your file paths
file_paths = {
   # "please": "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset/please.npy",
   # "sorry": "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset/sorry.npy",
   # "thanks": "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset/thanks.npy",
  #  "no": "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset/no.npy",
   # "yes": "/Users/shamakeskar/conferease/src/BrownBearTest/gesture_dataset/yes.npy"

   "we": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/we.npy",
   "review": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/review.npy",
   "emergency": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/emergency.npy",
   "process": "/Users/shamakeskar/conferease/src/BrownBearTest/airport_gesture_dataset/process.npy"
}

for gesture, path in file_paths.items():
    try:
        # Allow pickle loading
        data = np.load(path, allow_pickle=True)

        # Display basic stats
        print(f"Gesture: {gesture}")
        print(f"Number of Samples: {len(data)}")
       # print(f"Features per Sample: {data.shape[1]}")
      #  print(f"Min Values: {data.min(axis=0)[:5]}")  # First 5 features
      #  print(f"Max Values: {data.max(axis=0)[:5]}")  # First 5 features
      #  print(f"Mean Values: {data.mean(axis=0)[:5]}")  # First 5 features
      #  print("-" * 30)
# Check if data has "hands" and "face" keys
        sample = data[0]
        if isinstance(sample, dict):
            if "hands" in sample and "face" in sample:
                print("Sample includes both hands and face data.")
            elif "hands" in sample:
                print("Sample includes hands data only.")
            elif "face" in sample:
                print("Sample includes face data only.")
            else:
                print("Sample does not include hands or face data.")
        else:
            print("Data format is not a dictionary. Please verify.")

        print("-" * 30)
    except Exception as e:
        print(f"Error with gesture {gesture}: {e}")
