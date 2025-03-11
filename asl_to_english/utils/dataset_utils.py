import os
import h5py
import pandas as pd
from tqdm import tqdm

from models.sign_model import SignModel
from utils.landmark_utils import save_landmarks_from_video, load_landmarks_from_hdf5


def load_dataset(hdf5_path='data/dataset/landmarks.hdf5'):
    """
    Load or create dataset in HDF5 format
    
    :param hdf5_path: Path to the HDF5 file
    :return: List of processed video names
    """
    # Find all videos
    videos = [
        file_name.replace(".mp4", "")
        for root, dirs, files in os.walk(os.path.join("data", "videos"))
        for file_name in files
        if file_name.endswith(".mp4")
    ]

    # Check existing videos in HDF5
    try:
        with h5py.File(hdf5_path, 'r') as f:
            processed_videos = list(f.keys())
    except (FileNotFoundError, OSError):
        processed_videos = []
    # Create the dataset from the reference videos
    videos_not_in_dataset = list(set(videos).difference(set(processed_videos)))
    n = len(videos_not_in_dataset)
    
    if n > 0:
        print(f"\nExtracting landmarks from new videos: {n} videos detected\n")

        for idx in tqdm(range(n)):
            save_landmarks_from_video(videos_not_in_dataset[idx], hdf5_path)

    return videos


def load_reference_signs(videos, hdf5_path='data/dataset/landmarks.hdf5'):
    """
    Load reference signs from HDF5 file
    
    :param videos: List of video names
    :param hdf5_path: Path to the HDF5 file
    :return: DataFrame of reference signs
    """
    reference_signs = {"name": [], "sign_model": [], "distance": []}
    
    with h5py.File(hdf5_path, 'r') as f:
        for video_name in videos:
            sign_name = video_name.split("-")[0]
            
            # Load landmarks
            landmarks = load_landmarks_from_hdf5(video_name, hdf5_path)
            
            reference_signs["name"].append(sign_name)
            reference_signs["sign_model"].append(
                SignModel(
                    landmarks['left_hand'], 
                    landmarks['right_hand']
                )
            )
            reference_signs["distance"].append(0)
    
    reference_signs = pd.DataFrame(reference_signs, dtype=object)
    print(
        f'Dictionary count: {reference_signs[["name", "sign_model"]].groupby(["name"]).count()}'
    )
    return reference_signs
