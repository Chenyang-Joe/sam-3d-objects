import os
import numpy as np

animal_dir = "/local_data/cx2219/sam-3d-objects/notebook/results/animal_frames_1"
output_file = "/local_data/cx2219/sam-3d-objects/notebook/results/animal_sequence_1.obj"

# read all objs in animal_dir
# combine them into a frame sequence (one obj per frame), which can be opened in blender

# Get all .obj files and sort them
obj_files = []
for file in os.listdir(animal_dir):
    if file.endswith(".obj"):
        obj_files.append(os.path.join(animal_dir, file))

obj_files = sorted(obj_files, key = lambda x: int(os.path.basename(x).split('_')[0]))


# Use one animal per frame, generate a blend file that can animate the animal frames
# Note: This script needs to be run with Blender's Python: blender --background --python combine_animals.py

try:
    import bpy
except ImportError:
    print("This script must be run with Blender's Python!")
    print("Usage: blender --background --python combine_animals.py")
    exit(1)

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

print(f"\nCreating animation with {len(obj_files)} frames...")

# Import each mesh and set up keyframes
imported_objects = []
for frame_idx, obj_path in enumerate(obj_files):
    print(f"Frame {frame_idx + 1}/{len(obj_files)}: {os.path.basename(obj_path)}")
    
    # Import the obj file (Blender 4.0+ uses wm.obj_import instead of import_scene.obj)
    try:
        bpy.ops.wm.obj_import(filepath=obj_path)
    except AttributeError:
        # Fallback for older Blender versions
        bpy.ops.import_scene.obj(filepath=obj_path)
    
    # Get the imported object (should be the last selected)
    imported_obj = bpy.context.selected_objects[0]
    imported_objects.append(imported_obj)
    
    # Set visibility keyframes
    for i, obj in enumerate(imported_objects):
        # Make visible only on its designated frame
        obj.hide_viewport = (i != frame_idx)
        obj.hide_render = (i != frame_idx)
        
        # Insert keyframe for visibility
        obj.keyframe_insert(data_path="hide_viewport", frame=frame_idx + 1)
        obj.keyframe_insert(data_path="hide_render", frame=frame_idx + 1)
        
        # Also keyframe the previous and next frames to ensure proper visibility
        if frame_idx > 0:
            obj.hide_viewport = (i != frame_idx - 1)
            obj.hide_render = (i != frame_idx - 1)
            obj.keyframe_insert(data_path="hide_viewport", frame=frame_idx)
            obj.keyframe_insert(data_path="hide_render", frame=frame_idx)
        
        if frame_idx < len(obj_files) - 1:
            obj.hide_viewport = (i != frame_idx + 1)
            obj.hide_render = (i != frame_idx + 1)
            obj.keyframe_insert(data_path="hide_viewport", frame=frame_idx + 2)
            obj.keyframe_insert(data_path="hide_render", frame=frame_idx + 2)

# Set animation range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = len(obj_files)
bpy.context.scene.frame_current = 1

# Save the blend file
output_blend = output_file.replace('.obj', '.blend')
bpy.ops.wm.save_as_mainfile(filepath=output_blend)

print(f"\nAnimation created successfully!")
print(f"Blend file saved to: {output_blend}")
print(f"Total frames: {len(obj_files)}")
print(f"\nTo view: blender {output_blend}")