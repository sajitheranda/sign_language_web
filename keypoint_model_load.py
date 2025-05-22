import os
from pathlib import Path
import json
import cv2
from rtmlib import Wholebody, draw_skeleton
from config import DEVICE
# import torch


device = DEVICE
# if torch.cuda.is_available():
#     device = 'cuda'
# elif torch.backends.mps.is_available():  # for Apple Silicon Macs
#     device = 'mps'
# else:
#     device = 'cpu'

pose = "models/Keypoints_models/rtmw-x_simcc-cocktail13_pt-ucoco_270e-384x288-0949e3a9_20230925/20230928/rtmpose_onnx/rtmw-x_simcc-cocktail13_pt-ucoco_270e-384x288-0949e3a9_20230925/end2end.onnx"
pose_input_size = (288, 384)
det = "models/Keypoints_models/yolox_x_8xb8-300e_humanart-a39d44ed/20230928/yolox_onnx/yolox_x_8xb8-300e_humanart-a39d44ed/end2end.onnx"
det_input_size = (640, 640)
backend = 'onnxruntime'
openpose_skeleton = False

wholebody = Wholebody(
    to_openpose=openpose_skeleton,
    det=det,
    det_input_size=det_input_size,
    pose=pose,
    pose_input_size=pose_input_size,
    mode='balanced',
    backend=backend,
    device=device
)
