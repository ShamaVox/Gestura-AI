import bpy
import json
import math
from mathutils import Vector, Quaternion, Euler

def load_animation_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def get_bone_vector(pose_bones, bone_name):
    bone = pose_bones[bone_name]
    return bone.tail - bone.head

def calculate_rotation(vector1, vector2):
    return vector1.rotation_difference(vector2)

LEFT_ARM_OFFSET = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
RIGHT_ARM_OFFSET = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
LEFT_FOREARM_OFFSET = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')
RIGHT_FOREARM_OFFSET = Euler((math.radians(0), math.radians(0), math.radians(0)), 'XYZ')

def apply_rotation(bone, rotation, frame, is_arm=False, side='left'):
    if is_arm and side == 'left':
        # Apply additional rotation for arm bones
        correction = LEFT_ARM_OFFSET
        correction_quat = correction.to_quaternion()
        rotation = rotation @ correction_quat
    elif side == 'left' and not is_arm:
        correction = LEFT_FOREARM_OFFSET
        correction_quat = correction.to_quaternion()
        rotation = rotation @ correction_quat
    elif side == 'right' and is_arm:
        correction = RIGHT_ARM_OFFSET
        correction_quat = correction.to_quaternion()
        rotation = rotation @ correction_quat
    elif side == 'right' and not is_arm:
        correction = RIGHT_FOREARM_OFFSET
        correction_quat = correction.to_quaternion()
        rotation = rotation @ correction_quat

    if bone.rotation_mode == 'QUATERNION':
        bone.rotation_quaternion = rotation
        bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
    else:
        euler = rotation.to_euler(bone.rotation_mode)
        bone.rotation_euler = euler
        bone.keyframe_insert(data_path="rotation_euler", frame=frame)

def calculate_arm_rotation(shoulder, elbow, reference_vector):
    arm_vector = Vector(elbow) - Vector(shoulder)
    return calculate_rotation(reference_vector, arm_vector)

def animate_rig(armature, animation_data):
    pose_bones = armature.pose.bones
    
    bone_mapping = {
        'left_shoulder': 'mixamorig2:LeftArm',
        'right_shoulder': 'mixamorig2:RightArm',
        'left_elbow': 'mixamorig2:LeftForeArm',
        'right_elbow': 'mixamorig2:RightForeArm',
    }
    
    # Calculate reference vectors (T-pose)
    reference_vectors = {
        'mixamorig2:LeftArm': get_bone_vector(pose_bones, 'mixamorig2:LeftArm'),
        'mixamorig2:RightArm': get_bone_vector(pose_bones, 'mixamorig2:RightArm'),
        'mixamorig2:LeftForeArm': get_bone_vector(pose_bones, 'mixamorig2:LeftForeArm'),
        'mixamorig2:RightForeArm': get_bone_vector(pose_bones, 'mixamorig2:RightForeArm'),
    }
    
    # Calculate initial rotations (from T-pose to first frame)
    first_frame = animation_data['keyframes'][1]['landmarks']['pose']  # Using second frame as first actual pose
    initial_rotations = {
        'mixamorig2:LeftArm': calculate_arm_rotation(first_frame['left_shoulder'], first_frame['left_elbow'], reference_vectors['mixamorig2:LeftArm']),
        'mixamorig2:RightArm': calculate_arm_rotation(first_frame['right_shoulder'], first_frame['right_elbow'], reference_vectors['mixamorig2:RightArm']),
        'mixamorig2:LeftForeArm': calculate_arm_rotation(first_frame['left_elbow'], first_frame['left_wrist'], reference_vectors['mixamorig2:LeftForeArm']),
        'mixamorig2:RightForeArm': calculate_arm_rotation(first_frame['right_elbow'], first_frame['right_wrist'], reference_vectors['mixamorig2:RightForeArm']),
    }
    
    # Set up animation
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = len(animation_data['keyframes']) - 1
    
    # Animate each frame
    for frame_data in animation_data['keyframes'][1:]:  # Skip the first frame (T-pose)
        frame_number = frame_data['frame']
        landmarks = frame_data['landmarks']['pose']
        
        # Animate upper arms and forearms
        for side in ['left', 'right']:
            shoulder_bone = bone_mapping[f'{side}_shoulder']
            elbow_bone = bone_mapping[f'{side}_elbow']
            
            arm_rot = calculate_arm_rotation(
                landmarks[f'{side}_shoulder'], 
                landmarks[f'{side}_elbow'], 
                reference_vectors[shoulder_bone]
            )
            final_rot = initial_rotations[shoulder_bone].inverted() @ arm_rot
            apply_rotation(pose_bones[shoulder_bone], final_rot, frame_number, is_arm=True, side=side)
            
            forearm_rot = calculate_arm_rotation(
                landmarks[f'{side}_elbow'], 
                landmarks[f'{side}_wrist'], 
                reference_vectors[elbow_bone]
            )
            final_rot = initial_rotations[elbow_bone].inverted() @ forearm_rot
            apply_rotation(pose_bones[elbow_bone], final_rot, frame_number, is_arm=False, side=side)
    
    # Set interpolation method for smooth animation
    for fcurve in armature.animation_data.action.fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = 'LINEAR'


def main():
    animation_data = load_animation_data('/Users/admin/repos/conferease/animation_data.json')
    armature = bpy.data.objects['Armature.001']
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')
    animate_rig(armature, animation_data)
    bpy.context.view_layer.update()

if __name__ == "__main__":
    main()