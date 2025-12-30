import rerun as rr
import pickle
import numpy as np
import os
def compute_transformation_matrix(translation, scale, rotation):
    """
    Compute 4x4 transformation matrix from translation, scale, and rotation.
    
    Trimesh's apply_transform expects a LEFT multiplication matrix (v' = M @ v),
    which means the transformation is: Translate @ Rotate @ Scale
    
    This is the TRANSPOSE of PyTorch3D's Transform3d convention (which uses right multiplication).
    
    Args:
        translation: torch.Tensor (3,) or (N, 3) - translation vector [x, y, z]
        scale: torch.Tensor (3,) or (N, 3) - scale factors [sx, sy, sz]
        rotation: torch.Tensor (4,) or (N, 4) - quaternion [w, x, y, z]
        
    Returns:
        transform_matrix: (4, 4) numpy array - transformation matrix for trimesh
    """
    import torch
    from pytorch3d.transforms import quaternion_to_matrix
    
    # Convert to torch tensors if needed
    if not isinstance(translation, torch.Tensor):
        translation = torch.from_numpy(translation).float()
    if not isinstance(scale, torch.Tensor):
        scale = torch.from_numpy(scale).float()
    if not isinstance(rotation, torch.Tensor):
        rotation = torch.from_numpy(rotation).float()
    
    # Ensure correct shapes
    translation = translation.squeeze()
    scale = scale.squeeze()
    rotation = rotation.squeeze()
    
    # Convert quaternion to rotation matrix
    R = quaternion_to_matrix(rotation)  # (3, 3)
    
    # Create scale matrix
    S = torch.diag(scale)  # (3, 3)
    
    # For Trimesh (LEFT multiplication): we need the transpose
    # PyTorch3D uses: v' = v @ S @ R + t (right multiplication)
    # Trimesh uses: v' = (S @ R).T @ v + t (left multiplication)
    # So we need: (R @ S).T = S.T @ R.T = S @ R.T (since S is diagonal)
    
    RS = R @ S  # (3, 3) - same as PyTorch3D
    
    # Create 4x4 transformation matrix
    # For left multiplication by trimesh, we transpose the rotation-scale part
    T = torch.eye(4)
    T[:3, :3] = RS.T  # Transpose for left multiplication
    T[:3, 3] = translation
    
    return T.numpy()

if __name__ == "__main__":
    raw_data_path = "animal_raw_data.pkl"
    raw_data = pickle.load(open(raw_data_path, "rb"))
    save_dir = "./animal_sequence_rerun_example"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # rr.init("animal_sequence_rerun_example", spawn=False)

    for i, data in enumerate(raw_data):
        glb_mesh = data["glb"]
        translation = data["translation"] # 1,3
        scale = data["scale"] # 1,3
        rotation = data["rotation"] # 1,4

        transformation = compute_transformation_matrix(translation, scale, rotation)
        glb_mesh.apply_transform(transformation)

        glb_mesh.export(os.path.join(save_dir, f"animal_frame_{i:03d}.glb"))

        # Convert trimesh to rerun mesh
    #     vertices = glb_mesh.vertices
    #     faces = glb_mesh.faces

    #     rr.set_time("frame_idx", sequence=i)
    #     rr.log("one_animal", rr.Mesh3D(vertex_positions=vertices, triangle_indices=faces))
    #     print("processed frame ", i)
    # rr.save("animal_sequence_rerun_example.rerun")