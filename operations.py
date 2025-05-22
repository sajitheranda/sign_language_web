import torch

def flattern(keypoints):
    keypoints_tensor = torch.tensor(keypoints, dtype=torch.float32)

    x = keypoints_tensor[:, :, 0]
    y = keypoints_tensor[:, :, 1]
    keypoints_flattened = torch.cat([x, y], dim=1)
    keypoints = torch.cat((keypoints_flattened[:, 0:9], keypoints_flattened[:, 40:133], keypoints_flattened[:, 133:142], keypoints_flattened[:, 173:]),dim=1)
    return keypoints
