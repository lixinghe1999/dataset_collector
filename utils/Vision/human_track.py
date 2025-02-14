import cv2                                # state of the art computer vision algorithms library
import numpy as np                        # fundamental package for scientific computing
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API

def show_image(frameset):
    color_frame = frameset.get_color_frame()
    depth_frame = frameset.get_depth_frame()
    
    color = np.asanyarray(color_frame.get_data())
    color = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)

    colorizer = rs.colorizer()
    # Create alignment primitive with color as its target stream:
    align = rs.align(rs.stream.color)
    frameset = align.process(frameset)

    # Update color and depth frames:
    aligned_depth_frame = frameset.get_depth_frame()
    colorized_depth = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())

    # Show the two frames together:
    images = np.hstack((color, colorized_depth))

    plt.rcParams["axes.grid"] = False
    plt.rcParams['figure.figsize'] = [12, 6]
    plt.imshow(images)
    plt.show()


def mediapipe_facemesh(image):
  results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
  annotated_image = image.copy()
  for face_landmarks in results.multi_face_landmarks:
    print(face_landmarks)
    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_tesselation_style())
    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_contours_style())
    mp_drawing.draw_landmarks(
        image=annotated_image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_IRISES,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_iris_connections_style())
  cv2.imwrite('./test.png', annotated_image)
# Setup:
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_device_from_file("./dataset/tof/test.bag")
profile = pipe.start(cfg)

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):
  pipe.wait_for_frames()
  
# Store next frameset for later processing:
frameset = pipe.wait_for_frames()

# Cleanup:
pipe.stop()
print("Frames Captured")

# show_image(frameset)

import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

# For static images:
IMAGE_FILES = []
drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
with mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5) as face_mesh:
  
  image_color = frameset.get_color_frame()
  image = np.asanyarray(image_color.get_data())
  mediapipe_facemesh(image)