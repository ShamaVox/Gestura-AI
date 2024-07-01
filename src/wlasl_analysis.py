import pandas as pd
import json
import os
import shutil

def load_json_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        return json.load(file)

def find_video_ids(df, gloss):
    return df[df['gloss'] == gloss]['video_id'].tolist()

def word_to_number(word):
    number_mapping = {
        "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
        "ten": "10"
    }
    return number_mapping.get(word.lower(), word)

def move_and_rename_video(source_path, dest_path, word, index):
    if os.path.exists(source_path):
        word = word_to_number(word)
        new_filename = f"{word.lower()}_{index}.mp4"
        new_path = os.path.join(dest_path, new_filename)
        shutil.copy2(source_path, new_path)
        print(f"Moved and renamed: {new_filename}")
        return True
    else:
        print(f"Source file not found: {source_path}")
        return False

def main(json_file_path, source_folder, dest_folder):
    # Load the JSON data from file
    json_data = load_json_data(json_file_path)

    # Convert to DataFrame
    df = pd.json_normalize(json_data, 'instances', ['gloss'])

    # List of signs to search for
    signs = [
        "hello", "thank you", "you're welcome", "yes", "no", "please", "maybe",
        "i don't know", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "see", "look", "go", "come", "talk",
        "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"
    ]

    # Ensure destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    for sign in signs:
        video_ids = find_video_ids(df, sign)
        if video_ids:
            for index, video_id in enumerate(video_ids, start=1):
                source_path = os.path.join(source_folder, f"{video_id}.mp4")
                success = move_and_rename_video(source_path, dest_folder, sign, index)
                if success:
                    print(f"Processed {sign} (ID: {video_id})")
                if index >= 3:  # Limit to 3 videos per sign
                    break
        else:
            print(f"No videos found for: {sign}")

    print("\nVideo processing completed.")

if __name__ == "__main__":
    json_file_path = "/Users/admin/repos/conferease/WLASL/start_kit/WLASL_v0.3.json"
    source_folder = "/Users/admin/repos/conferease/WLASL/start_kit/raw_videos"
    dest_folder = "/Users/admin/repos/conferease/videos"
    main(json_file_path, source_folder, dest_folder)