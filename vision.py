from utils.Vision.realsense import tof_stream, tof_load, show_frame, face_depth, show_output
from utils.Vision.human_track import mediapipe_facemesh, landmarks_3d, normal_vector
import numpy as np
import matplotlib.pyplot as plt
import argparse
if __name__ == '__main__':
    # tof_stream()
    pipe, depth_scale = tof_load('dataset/tof/test3.bag')
    for i in range(5, 200):
        frameset = pipe.wait_for_frames()

        landmarks, image = mediapipe_facemesh(frameset, max_num_faces=1, plot=True)
        landmarks = [np.array([[lm.x, lm.y, lm.z] for lm in landmark.landmark]) for landmark in landmarks]
        landmarks = np.array(landmarks)
        bbox = np.concatenate([landmarks[:, :, 0].min(axis=1, keepdims=True), landmarks[:, :, 1].min(axis=1, keepdims=True),
                            landmarks[:, :, 0].max(axis=1, keepdims=True), landmarks[:, :, 1].max(axis=1, keepdims=True)], axis=1)
        face_depths = face_depth(frameset, bbox, depth_scale)

        normal_vecs = np.array([normal_vector(landmarks[face_id]) for face_id in range(len(landmarks))])
        # landmarks_3d(landmarks[0], normal_vecs[0])
        # show_frame(frameset) # visualize one frame 
        show_output(frameset, bbox, face_depths, normal_vecs)        
    pipe.stop()
