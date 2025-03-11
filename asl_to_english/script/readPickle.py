import pickle
import os
import numpy as np

def load_pickle_file(file_path):
    """
    Load pickle file, convert to numpy array, and print shape
    
    :param file_path: Path to the pickle file to be loaded
    """
    try:
        with open(file_path, 'rb') as file:
            data = pickle.load(file)
            data_array = np.array(data)
            print(f"Contents of {os.path.basename(file_path)}:")
            print(f"Shape: {data_array.shape}")
            print("Data[0][0]:", data_array[0][0])
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
    except pickle.UnpicklingError:
        print(f"Error: Unable to unpickle file {file_path}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    # Example usage - you can modify the path as needed
    pickle_files = [
        os.path.join('data', 'dataset', sign_name, video_name, f'pose_{video_name}.pickle')
        for sign_name in os.listdir(os.path.join('data', 'dataset')) if sign_name != '.gitkeep'
        for video_name in os.listdir(os.path.join('data', 'dataset', sign_name))
    ]
    
    for file_path in pickle_files:
        load_pickle_file(file_path)

if __name__ == "__main__":
    main()
