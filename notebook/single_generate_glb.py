import os
import uuid
import imageio
import numpy as np
from IPython.display import Image as ImageDisplay
import trimesh
import pickle

from inference import Inference, ready_gaussian_for_video_rendering, load_image, load_masks, display_image, make_scene, render_video, interactive_visualizer, load_mask
from pytorch3d.transforms import quaternion_to_matrix
from sam3d_objects.data.dataset.tdfy.transforms_3d import compose_transform
import torch
import numpy as np


def read_animal_pictures(raw_dir):
    image_paths = []
    mask_paths = []
    for file_name in os.listdir(raw_dir):
        if file_name.endswith("_rgb.png"):
            image_paths.append(os.path.join(raw_dir, file_name))
        elif file_name.endswith("_masked.png"):
            mask_paths.append(os.path.join(raw_dir, file_name))

    # sort in terms of int(lambda.split('_')[0])
    image_paths.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))
    mask_paths.sort(key=lambda x: int(os.path.basename(x).split('_')[0]))
    
    return image_paths, mask_paths


def create_animated_glb(mesh_list):
    # Different topology - export as multi-mesh scene
    scene = trimesh.Scene()
    
    for i, mesh in enumerate(mesh_list):
        # Add each mesh to the scene
        scene.add_geometry(mesh, node_name=f"frame_{i:03d}", geom_name=f"mesh_{i:03d}")
    return scene


if __name__ == "__main__":
    os.environ["CUDA_VISIBLE_DEVICES"] = "6"
    os.environ["GRADIO_TEMP_DIR"] = "/scratch/cx2219/gradio_temp"

    PATH = os.getcwd()
    TAG = "hf"
    config_path = f"{PATH}/checkpoints/{TAG}/pipeline.yaml"
    inference = Inference(config_path, compile=False)

    image_folder = "/scratch/cx2219/animal4d/pack_data/deer/pictures/_0LBZdvCOU8_020_001"
    save_folder = "/scratch/cx2219/codebase/sam-3d-objects/notebook/results/animal_frames/"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    image_paths, mask_paths = read_animal_pictures(image_folder)



    mesh_list = []
    # raw_data = []
    for example_image_path, example_mask_path in zip(image_paths, mask_paths):
        image = load_image(example_image_path)
        mask = [load_mask(example_mask_path)]

        outputs = inference(image, mask[0], seed=42)

        # need to convert tensors to cpu numpy for pickle
        data_to_save = {
            "glb": outputs["glb"],
            "translation": np.array(outputs["translation"].detach().cpu()),
            "scale": np.array(outputs["scale"].detach().cpu()),
            "rotation": np.array(outputs["rotation"].detach().cpu()),
        }

        # raw_data.append(data_to_save)

        glb_mesh = outputs["glb"]
        translation = outputs["translation"] # 1,3
        scale = outputs["scale"] # 1,3
        rotation = outputs["rotation"] # 1,4

        mesh_now = glb_mesh.copy()
        rotation_matrix = quaternion_to_matrix(rotation)
        tfm = compose_transform(scale=scale, rotation=rotation_matrix, translation=translation)
        points = mesh_now.vertices
        # this is z-up right-handed, so need to convert to y-up left-handed for pytorch3d
        points_pytorch = torch.from_numpy(points).float().cuda()
        # Convert from z-up to y-up: rotate around x-axis by -90 degrees
        points_pytorch = points_pytorch @ torch.tensor([[1, 0, 0], [0, 0, -1], [0, 1, 0]], device=points_pytorch.device, dtype=points_pytorch.dtype).T
        points_world = tfm.transform_points(points_pytorch)
        vertices = points_world.cpu().numpy()

        z_lower_bounding = np.min(vertices[:, 2])
        vertices[:, 2] -= z_lower_bounding
        mesh_now.vertices = vertices

        mesh_list.append(mesh_now)
        mesh_now.export(save_folder+os.path.basename(example_image_path).replace("_rgb.png", "_align.glb"))


    
    # pickle.dump(raw_data, open("animal_raw_data.pkl", "wb"))
    # aniamted_scene = create_animated_glb(mesh_list)
    # aniamted_scene.export("animal_animation.glb")