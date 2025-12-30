import os
import numpy as np

animal_dir = "/local_data/cx2219/sam-3d-objects/notebook/results/animal_frames_2"
output_file = "/local_data/cx2219/sam-3d-objects/notebook/results/animal_frames_2.blend"

# read all glb files in animal_dir
# combine them into a frame sequence (one glb per frame), which can be opened in blender

# Get all .glb files and sort them
glb_files = []
for file in os.listdir(animal_dir):
    if file.endswith(".glb") or file.endswith(".gltf"):
        glb_files.append(os.path.join(animal_dir, file))

glb_files = sorted(glb_files, key=lambda x: int(os.path.basename(x).split('_')[0]))


# Use one animal per frame, generate a blend file that can animate the animal frames
# Note: This script needs to be run with Blender's Python: blender --background --python combine_animals_glb.py

try:
    import bpy
except ImportError:
    print("This script must be run with Blender's Python!")
    print("Usage: blender --background --python combine_animals_glb.py")
    exit(1)

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

print(f"\nCreating animation with {len(glb_files)} frames...")

# Import each mesh and set up keyframes
imported_objects = []
for frame_idx, glb_path in enumerate(glb_files):
    print(f"Frame {frame_idx + 1}/{len(glb_files)}: {os.path.basename(glb_path)}")
    
    # Import the glb file (Blender 4.0+ uses wm.gltf_import)
    try:
        bpy.ops.import_scene.gltf(filepath=glb_path)
    except AttributeError:
        print(f"Error: Could not import {glb_path}")
        continue
    
    # Get all imported objects from this import
    current_objects = bpy.context.selected_objects[:]
    imported_objects.append(current_objects)
    
    # Set visibility keyframes for all previously imported objects
    for i, obj_group in enumerate(imported_objects):
        for obj in obj_group:
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
            
            if frame_idx < len(glb_files) - 1:
                obj.hide_viewport = (i != frame_idx + 1)
                obj.hide_render = (i != frame_idx + 1)
                obj.keyframe_insert(data_path="hide_viewport", frame=frame_idx + 2)
                obj.keyframe_insert(data_path="hide_render", frame=frame_idx + 2)

# Set animation range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = len(glb_files)
bpy.context.scene.frame_current = 1

# Save the blend file
bpy.ops.wm.save_as_mainfile(filepath=output_file)

print("\nAnimation created successfully!")
print(f"Blend file saved to: {output_file}")
print(f"Total frames: {len(glb_files)}")
print(f"\nTo view: blender {output_file}")
