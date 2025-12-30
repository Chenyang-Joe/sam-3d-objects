import os
import trimesh
import pickle

from inference import Inference, ready_gaussian_for_video_rendering, load_image, load_masks, display_image, make_scene, render_video, interactive_visualizer
from pytorch3d.transforms import quaternion_to_matrix
from sam3d_objects.data.dataset.tdfy.transforms_3d import compose_transform
import torch
from sam3d_objects.utils.visualization import SceneVisualizer
import numpy as np


if __name__ == "__main__":
    outputs_path = "/local_data/cx2219/sam-3d-objects/notebook/results/shutterstock_stylish_kidsroom_1640806567_multi_object/shutterstock_stylish_kidsroom_1640806567_outputs.pkl"
    outputs = pickle.load(open(outputs_path, "rb"))

    PATH = os.getcwd()
    IMAGE_NAME = "shutterstock_stylish_kidsroom_1640806567"

    scene_gs = make_scene(*outputs)
    # scene_gs = ready_gaussian_for_video_rendering(scene_gs)


    # export gaussian splatting (as point cloud)
    scene_gs.save_ply(f"{PATH}/gaussians/multi/{IMAGE_NAME}.ply")

    for i, output in enumerate(outputs):
        print(output["translation"], output["scale"], output["rotation"])
        output["gaussian"][0].save_ply(
            f"{PATH}/gaussians/multi/{IMAGE_NAME}_object_{i}.ply"
        )