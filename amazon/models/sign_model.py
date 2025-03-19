from typing import List

import numpy as np

from models.hand_model import HandModel


class SignModel(object):
    def __init__(
        self, left_hand_list: List[List[float]], right_hand_list: List[List[float]], 
        pose_list: List[List[float]] = None
    ):
        """
        Params
            x_hand_list: List of all landmarks for each frame of a video
            pose_list: List of all pose landmarks for each frame of a video
        Args
            has_x_hand: bool; True if x hand is detected in the video, otherwise False
            xh_embedding: ndarray; Array of shape (n_frame, nb_connections * nb_connections)
            has_pose: bool; True if pose is detected in the video, otherwise False
            pose_embedding: ndarray; Array of shape (feature_dimension,) representing the entire video
        """
        self.has_left_hand = np.sum(left_hand_list) != 0
        self.has_right_hand = np.sum(right_hand_list) != 0
        self.has_pose = pose_list is not None and np.sum(pose_list) != 0

        self.lh_embedding = self._get_embedding_from_landmark_list(left_hand_list)
        self.rh_embedding = self._get_embedding_from_landmark_list(right_hand_list)
        
        # Process pose landmarks if available
        self.pose_embedding = None
        if self.has_pose:
            self.pose_embedding = self._get_pose_movement_embedding(pose_list)

    @staticmethod
    def _get_embedding_from_landmark_list(
        hand_list: List[List[float]],
    ) -> List[List[float]]:
        """
        Params
            hand_list: List of all landmarks for each frame of a video
        Return
            Array of shape (n_frame, nb_connections * nb_connections) containing
            the feature_vectors of the hand for each frame
        """
        embedding = []
        for frame_idx in range(len(hand_list)):
            if np.sum(hand_list[frame_idx]) == 0:
                continue

            hand_gesture = HandModel(hand_list[frame_idx])
            embedding.append(hand_gesture.feature_vector)
        return embedding
    
    @staticmethod
    def _get_pose_movement_embedding(
        pose_list: List[List[float]],
    ) -> np.ndarray:
        """
        Extract a single embedding vector representing pose movement throughout the video.
        
        Params
            pose_list: List of all pose landmarks for each frame of a video
                       Each element is a flattened list of (x,y,z) coordinates for 33 pose landmarks
        Return
            A single vector representing the pose movement characteristics across the entire video
        """
        if len(pose_list) < 2:
            return np.array([])
            
        # Convert to numpy array for easier manipulation
        pose_array = np.array(pose_list)
        
        # Head landmarks indices (0-10): nose, eyes, ears, mouth
        # 0: nose, 1-6: eyes, 7-8: ears, 9-10: mouth
        head_indices = list(range(11))  # 0 to 10
        
        # Calculate frame-by-frame movement features
        frame_features = []
        
        for i in range(1, len(pose_array)):
            # Skip if either current or previous frame has no valid landmarks
            if np.sum(pose_array[i]) == 0 or np.sum(pose_array[i-1]) == 0:
                continue
                
            # Calculate the difference between current and previous frame
            # Reshape to (33, 3) for 33 landmarks with x,y,z coordinates
            prev_frame = pose_array[i-1].reshape(-1, 3)
            curr_frame = pose_array[i].reshape(-1, 3)
            # Filter only head landmarks
            prev_frame_head = prev_frame[head_indices]
            curr_frame_head = curr_frame[head_indices]
            
            # Calculate displacement vectors for head landmarks only
            displacement = np.abs(curr_frame_head - prev_frame_head)
            
            # Flatten the features
            features = np.concatenate([
                displacement.flatten(),                # Raw displacement
            ])
            
            frame_features.append(features)
        
        if not frame_features:
            return np.array([])
        
            
        # Aggregate frame features into a single video-level embedding
        frame_features = np.array(frame_features)
        
        # # Create a single vector with statistical features across all frames
        # video_embedding = np.concatenate([
        #     np.mean(frame_features, axis=0),      # Mean of each feature
        #     np.std(frame_features, axis=0),       # Standard deviation
        #     np.max(frame_features, axis=0),       # Maximum values
        #     np.min(frame_features, axis=0),       # Minimum values
        #     np.median(frame_features, axis=0),    # Median values
        #     np.percentile(frame_features, 25, axis=0),  # 25th percentile
        #     np.percentile(frame_features, 75, axis=0)   # 75th percentile
        # ])
        video_embedding = np.sum(frame_features, axis=0)
        return video_embedding
