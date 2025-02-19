import cv2                                # state of the art computer vision algorithms library
import numpy as np                        # fundamental package for scientific computing
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
import pyrealsense2 as rs                 # Intel RealSense cross-platform open-source API



def mediapipe_facemesh(frameset, max_num_faces=1, plot=False):
    import mediapipe as mp
    image_color = frameset.get_color_frame()
    image = np.asanyarray(image_color.get_data())
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_face_mesh = mp.solutions.face_mesh
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=True,
        max_num_faces=max_num_faces,
        refine_landmarks=True,
        min_detection_confidence=0.5)
    results = face_mesh.process(image)
    multi_face_landmarks = results.multi_face_landmarks
    annotated_image = image.copy()
    if plot:
      for face_landmarks in multi_face_landmarks:
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
    return multi_face_landmarks, annotated_image

def normal_vector(landmarks):
    from .facemesh import MESH_ANNOTATIONS

    silhouette_indices = MESH_ANNOTATIONS["silhouette"]
    silhouette_points = landmarks[silhouette_indices]
    # Calculate the normal vector of the plane
    # https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points
    A = np.cov(silhouette_points.T)
    _, _, V = np.linalg.svd(A)
    normal = V[2]
    return normal

def landmarks_3d(landmarks, normal_vec):
      face_mean = np.mean(landmarks, axis=0)
      # 3D scatter plot
      fig = plt.figure()
      ax = fig.add_subplot(111, projection='3d')
      # plot the normal vector
      ax.quiver(face_mean[0], face_mean[1], face_mean[2], normal_vec[0], normal_vec[1], normal_vec[2], color='r')

      ax.scatter(landmarks[:, 0], landmarks[:, 1], landmarks[:, 2])
      from .facemesh import MESH_ANNOTATIONS

      silhouette_indices = MESH_ANNOTATIONS["silhouette"]
      ax.scatter(landmarks[silhouette_indices, 0], landmarks[silhouette_indices, 1], landmarks[silhouette_indices, 2], color='r')

      ax.set_xlabel('X')
      ax.set_ylabel('Y')
      ax.set_zlabel('Z')
      plt.show()

    
