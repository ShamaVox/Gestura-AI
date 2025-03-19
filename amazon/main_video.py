import cv2
import mediapipe
import sys
import argparse

from utils.dataset_utils import load_dataset, load_reference_signs
from utils.mediapipe_utils import mediapipe_detection
from sign_recorder import SignRecorder
from webcam_manager import WebcamManager


def process_video(video_path, reference_signs):
    # Object that stores mediapipe results and computes sign similarities
    sign_recorder = SignRecorder(reference_signs)

    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Set up the Mediapipe environment
    with mediapipe.solutions.holistic.Holistic(
        min_detection_confidence=0.5, min_tracking_confidence=0.5
    ) as holistic:
        sign_recorder.record()
        while cap.isOpened():
            # Read feed
            ret, frame = cap.read()
            
            # Break the loop if no more frames
            if not ret:
                break

            # Make detections
            _, results = mediapipe_detection(frame, holistic)

            # Process results
            sign_recorder.process_results(results)

        cap.release()
        cv2.destroyAllWindows()
    sign_recorder.stop_recording(verbose=False)
    # Process all results and get the predicted sign
    predicted_sign, _ = sign_recorder.process_results({})
    print(f"Predicted Sign: {predicted_sign}")
    # print("Reference Signs Distances:")
    # print(sign_recorder.reference_signs)


def main():
    # Create parser for command-line arguments
    parser = argparse.ArgumentParser(description='Process sign language video')
    parser.add_argument('video_path', type=str, help='Path to the input video file')
    
    # Parse arguments
    args = parser.parse_args()

    # Create dataset of the videos where landmarks have not been extracted yet
    videos = load_dataset()

    # Create a DataFrame of reference signs (name: str, model: SignModel, distance: int)
    reference_signs = load_reference_signs(verbose=False)

    # Process the specified video
    process_video(args.video_path, reference_signs)


if __name__ == "__main__":
    main()