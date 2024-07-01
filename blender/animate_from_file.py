import bpy
import json
import mathutils

def interpolate_bone(parent_pos, child_pos, factor):
    return parent_pos.lerp(child_pos, factor)

# Load the animation data
with open('/Users/admin/repos/conferease/animation_data.json', 'r') as f:
    animation_data = json.load(f)

# Get the armature
armature = bpy.data.objects['Armature']  # Adjust name if different

# Define bone mapping and hierarchy
bone_mapping = {
    'head': 'Head',
    'left_shoulder': 'LeftShoulder',
    'right_shoulder': 'RightShoulder',
    'left_elbow': 'LeftArm',
    'right_elbow': 'RightArm',
    'left_wrist': 'LeftForeArm',
    'right_wrist': 'RightForeArm',
    'left_hip': 'LeftUpLeg',
    'right_hip': 'RightUpLeg'
}

bone_hierarchy = {
    'Hips': ['Spine', 'Spine1', 'Spine2', 'Neck', 'Head'],
    'LeftShoulder': ['LeftArm', 'LeftForeArm', 'LeftHand'],
    'RightShoulder': ['RightArm', 'RightForeArm', 'RightHand'],
    'LeftUpLeg': ['LeftLeg', 'LeftFoot'],
    'RightUpLeg': ['RightLeg', 'RightFoot']
}

# Set animation parameters
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_end = len(animation_data['keyframes']) - 1

# Animate the avatar
for frame, keyframe in enumerate(animation_data['keyframes']):
    bpy.context.scene.frame_set(frame)
    
    pose_data = keyframe['landmarks']['pose']
    
    # Set positions for tracked bones
    for landmark, bone_name in bone_mapping.items():
        if landmark in pose_data:
            bone = armature.pose.bones[bone_name]
            coords = pose_data[landmark]
            bone.location = (coords[0], coords[2], coords[1])
            bone.keyframe_insert(data_path="location", frame=frame)
    
    # Interpolate spine bones
    if 'left_hip' in pose_data and 'right_hip' in pose_data and 'head' in pose_data:
        hips_pos = (mathutils.Vector(pose_data['left_hip']) + mathutils.Vector(pose_data['right_hip'])) / 2
        head_pos = mathutils.Vector(pose_data['head'])
        spine_bones = bone_hierarchy['Hips']
        for i, bone_name in enumerate(spine_bones):
            factor = (i + 1) / (len(spine_bones) + 1)
            bone = armature.pose.bones[bone_name]
            bone.location = interpolate_bone(hips_pos, head_pos, factor)
            bone.keyframe_insert(data_path="location", frame=frame)
    
    # Interpolate arm and leg bones
    for parent, children in bone_hierarchy.items():
        if parent in bone_mapping.values():
            parent_bone = armature.pose.bones[parent]
            parent_pos = parent_bone.head
            end_pos = parent_bone.tail
            for i, child_name in enumerate(children):
                factor = (i + 1) / (len(children) + 1)
                child_bone = armature.pose.bones[child_name]
                child_bone.location = interpolate_bone(parent_pos, end_pos, factor)
                child_bone.keyframe_insert(data_path="location", frame=frame)

# Set interpolation method for smooth animation
for fc in armature.animation_data.action.fcurves:
    for kf in fc.keyframe_points:
        kf.interpolation = 'LINEAR'

print("Animation complete!")