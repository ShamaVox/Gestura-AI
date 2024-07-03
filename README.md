# conferease

# To run the Unity applications with animation selection
1. Open `unity/{Unity Project}/Assets/Scene.unity` in Unity
2. Press play in top middle
3. Select animation from drop down
4. Press play button

# To auto-generate animations from videos
1. Install requirements with `pip install -r requirements.txt`
2. To create animation_data.json
    Two options:
        Option 1: 
            Open `conferease` folder in VS Code
            Open `src/process_vid.py` file then `Run and Debug`
        Option 2: Run `python src/process_vid.py` from terminal
    This will create the file `animation_data.json`
3. To view animation and extracted keypoints
    Two options:
        Option 1: 
            From `conferease` folder in VS Code
            Open `src/view_landmakrs.py` file then `Run and Debug`
        Option 2: Run `python src/view_landmakrs.py` from terminal
    This will open a window to view animation and keypoints

# To run transfer of keypoints to animations in blender
1. Open `blender/auto_animations.blend` in Blender
2. Open the `Scripting` tab
3. In the drop-down, select `reset_pose.py` and Run
4. In the drop-down, select `animate.py` and Run
5. Open the `Animation` tab. At the bottom of the screen, there is a play button to play the animation.