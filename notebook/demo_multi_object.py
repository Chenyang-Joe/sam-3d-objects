# Copyright (c) Meta Platforms, Inc. and affiliates.
# Set CUDA_VISIBLE_DEVICES to specify which GPUs to use
import os
import trimesh
from tqdm import tqdm
import torch
os.environ["CUDA_VISIBLE_DEVICES"] = "4"
os.environ["GRADIO_TEMP_DIR"] = "/local_data/cx2219/gradio_temp"
import pickle

import os
import uuid
import imageio
import numpy as np
from IPython.display import Image as ImageDisplay

from inference import Inference, ready_gaussian_for_video_rendering, load_image, load_masks, display_image, make_scene, render_video, interactive_visualizer
from pytorch3d.transforms import quaternion_to_matrix
from sam3d_objects.data.dataset.tdfy.transforms_3d import compose_transform

PATH = os.getcwd()
TAG = "hf"
config_path = f"{PATH}/checkpoints/{TAG}/pipeline.yaml"
inference = Inference(config_path, compile=False)

IMAGE_PATH = f"{PATH}/notebook/images/shutterstock_stylish_kidsroom_1640806567/image.png"
IMAGE_NAME = os.path.basename(os.path.dirname(IMAGE_PATH))

image = load_image(IMAGE_PATH)
masks = load_masks(os.path.dirname(IMAGE_PATH), extension=".png")
display_image(image, masks)

outputs = [inference(image, mask, seed=42) for mask in masks[:1]]
# outputs = [inference(image, mask, seed=42) for mask in masks]


# The GLB mesh is in LOCAL coordinates (normalized space -0.5 to 0.5)
# We need to apply the transformation to convert to WORLD coordinates
# Note: layout_post_optimization is NOT used (config sets it to None)
# So we use the raw pose predictions from the model

aligned_mesh_list = []

save_dir = f"./results/{IMAGE_NAME}_multi_object"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


deform_info = []
for i, output in tqdm(enumerate(outputs)):
    glb_mesh = output["glb"].copy()
    translation = output["translation"]
    scale = output["scale"]
    rotation = output["rotation"]
    deform_info.append({
        "translation": translation.cpu().numpy(),
        "scale": scale.cpu().numpy(),
        "rotation": rotation.cpu().numpy()
    })
    
    glb_mesh.export(os.path.join(save_dir, f"{IMAGE_NAME}_{i}_raw.glb"))

    # Use the codebase's compose_transform function
    rotation_matrix = quaternion_to_matrix(rotation)
    tfm = compose_transform(scale=scale, rotation=rotation_matrix, translation=translation)
    points = glb_mesh.vertices
    points_pytorch = torch.from_numpy(points).to(torch.float32).cuda()
    points_pytorch = points_pytorch @ torch.tensor([[1, 0, 0], [0, 0, -1], [0, 1, 0]], device=points_pytorch.device, dtype=points_pytorch.dtype).T

    points_world = tfm.transform_points(points_pytorch)
    glb_mesh.vertices = points_world.cpu().numpy()

    glb_mesh.export(os.path.join(save_dir, f"{IMAGE_NAME}_{i}_align.glb"))
    aligned_mesh_list.append(glb_mesh)

glb_scene = trimesh.Scene()
for mesh in tqdm(aligned_mesh_list):
    glb_scene.add_geometry(mesh)

pickle.dump(deform_info, open(f"{save_dir}/{IMAGE_NAME}_deform_info.pkl", "wb"))
pickle.dump(outputs, open(f"{save_dir}/{IMAGE_NAME}_outputs.pkl", "wb"))
glb_scene.export(f"{save_dir}/{IMAGE_NAME}_combined_aligned.glb")

