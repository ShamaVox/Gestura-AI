import pandas as pd
from fastdtw import fastdtw
import numpy as np
from models.sign_model import SignModel


def dtw_distances(recorded_sign: SignModel, reference_signs: pd.DataFrame):
    """
    Use DTW to compute similarity between the recorded sign & the reference signs

    :param recorded_sign: a SignModel object containing the data gathered during record
    :param reference_signs: pd.DataFrame
                            columns : name, dtype: str
                                      sign_model, dtype: SignModel
                                      distance, dtype: float64
    :return: Return a sign dictionary sorted by the distances from the recorded sign
    """
    # Embeddings of the recorded sign
    rec_left_hand = recorded_sign.lh_embedding
    rec_right_hand = recorded_sign.rh_embedding
    rec_pose = recorded_sign.pose_embedding
    rec_sum_pose = np.sum(rec_pose)
    # print(f"rec_sum_pose: {rec_sum_pose}")

    for idx, row in reference_signs.iterrows():
        # Initialize the row variables
        ref_sign_name, ref_sign_model, _ = row
        ref_left_hand = ref_sign_model.lh_embedding
        ref_right_hand = ref_sign_model.rh_embedding
        ref_pose = ref_sign_model.pose_embedding
        
        # Reset distance for this reference sign
        row["distance"] = 0
        
        # Compute raw DTW distances for each modality
        left_hand_distance = np.inf
        right_hand_distance = np.inf
        pose_distance = np.inf
        
        # Compute DTW for available hands
        if recorded_sign.has_left_hand and ref_sign_model.has_left_hand:
            left_hand_distance = list(fastdtw(rec_left_hand, ref_left_hand))[0]
        
        if recorded_sign.has_right_hand and ref_sign_model.has_right_hand:
            right_hand_distance = list(fastdtw(rec_right_hand, ref_right_hand))[0]
            
        # Compute DTW for head pose movement if available
        if recorded_sign.has_pose and ref_sign_model.has_pose and len(rec_pose) > 0 and len(ref_pose) > 0:
            ref_sum_pose = np.sum(ref_pose)
            pose_distance = np.abs(rec_sum_pose - ref_sum_pose) * 1000
        # # Print all distances in a same line
        # print(f"Pose Distance: {pose_distance} of {ref_sign_name}, Left Hand Distance: {left_hand_distance} of {ref_sign_name}, Right Hand Distance: {right_hand_distance} of {ref_sign_name}")
        # Compute overall distance with weights
        hand_weight = 1.0
        head_pose_weight = 1
        
        # Compute weighted distance
        distances = [
            left_hand_distance * hand_weight if left_hand_distance != np.inf else 0,
            right_hand_distance * hand_weight if right_hand_distance != np.inf else 0,
            pose_distance * head_pose_weight if pose_distance != np.inf else 0
        ]
        # print(f"Distances: {distances} of {ref_sign_name}")
        
        # Compute weights for normalization
        weights = [
            hand_weight if recorded_sign.has_left_hand and ref_sign_model.has_left_hand else 0,
            hand_weight if recorded_sign.has_right_hand and ref_sign_model.has_right_hand else 0,
            head_pose_weight if recorded_sign.has_pose and ref_sign_model.has_pose and len(rec_pose) > 0 and len(ref_pose) > 0 else 0
        ]
        # Compute length of the reference sign
        ref_length = max(len(ref_left_hand), len(ref_right_hand))
        
        # Compute weighted average distance
        total_weight = sum(weights)
        row["distance"] = sum(distances) / max(total_weight, 1)
        row["distance"] = row["distance"] / ref_length


    return reference_signs.sort_values(by=["distance"])
