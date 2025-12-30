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
    mesh_dir = "/local_data/cx2219/sam-3d-objects/notebook/results/shutterstock_stylish_kidsroom_1640806567_multi_object"
    transform_info = "/local_data/cx2219/sam-3d-objects/notebook/results/shutterstock_stylish_kidsroom_1640806567_multi_object/shutterstock_stylish_kidsroom_1640806567_deform_info.pkl"


    mesh_path_list = []
    for file in os.listdir(mesh_dir):
        if file.endswith("_raw.glb"):
            mesh_path_list.append(os.path.join(mesh_dir, file))

    mesh_path_list = sorted(mesh_path_list, key = lambda x: int(x.split("_")[-2]))
    
    mesh_list = []
    for mesh_path in mesh_path_list:
        mesh = trimesh.load(mesh_path)
        # load as a mesh not a scene
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
        mesh_list.append(mesh)

    transform_info = pickle.load(open(transform_info, "rb"))

    transformed_meshes = [] 
    for transform, glb_mesh in zip(transform_info[2:3] ,mesh_list[2:3]):


        translation = torch.from_numpy(transform["translation"]).cuda()
        scale = torch.from_numpy(transform["scale"]).cuda()
        rotation = torch.from_numpy(transform["rotation"]).cuda()


        # print(translation, scale, rotation)
        # print("Translation:", translation)
        # print("Scale:", scale)
        # print("Rotation (quat):", rotation)

        mesh_now = glb_mesh.copy()

        # Use the codebase's compose_transform function
        rotation_matrix = quaternion_to_matrix(rotation)
        tfm = compose_transform(scale=scale, rotation=rotation_matrix, translation=translation)
        points = mesh_now.vertices
        points_torch = torch.from_numpy(points).to(torch.float32).cuda()
        points_world = tfm.transform_points(points_torch)
        mesh_now.vertices = points_world.cpu().numpy()

        print(tfm.get_matrix())

        # mesh_now.vertices = SceneVisualizer.object_pointcloud(
        #     points_local=torch.from_numpy(mesh_now.vertices).float().cuda().unsqueeze(0),  # mesh vertices as points
        #     quat_l2c=rotation,
        #     trans_l2c=translation,
        #     scale_l2c=scale,
        # ).points_list()[0].cpu().numpy()

        # print(mesh_now.vertices[:5])

    #     transformed_meshes.append(mesh_now)
    
    # # export all transformed meshes into a single glb
    # # combined_mesh = trimesh.util.concatenate(transformed_meshes)
    # # combined_mesh.export(os.path.join(mesh_dir, "combined_transformed_mesh.glb"))