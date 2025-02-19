import numpy as np
import cv2
import matplotlib.pyplot as plt


def calculate_angles(image, fx, fy, cx, cy):
    height, width = image.shape[:2]
    angles = np.zeros((height, width, 3), dtype=np.float32)
    
    for y in range(height):
        for x in range(width):
            # 归一化坐标
            xn = (x - cx) / fx
            yn = (y - cy) / fy
            zn = 1.0
            
            # 计算角度 (弧度)
            theta_x = np.degrees(np.arctan2(xn, zn))
            theta_y = np.degrees(np.arctan2(yn, zn))
            angle = np.degrees(np.arccos(zn / np.sqrt(xn**2 + yn**2 + zn**2)))

            angles[y, x, 0] = theta_x
            angles[y, x, 1] = theta_y
            angles[y, x ,2] = angle

    return angles

def visualize_angles(angles):
    plt.imshow(angles[:,:,0], cmap='jet')
    plt.colorbar(label='Angle with X-axis')
    plt.title('Pixel Angles with X-axis')
    plt.show()
    
    plt.imshow(angles[:,:,1], cmap='jet')
    plt.colorbar(label='Angle with Y-axis')
    plt.title('Pixel Angles with Y-axis')
    plt.show()
    
    plt.imshow(angles[:,:,2], cmap='jet')
    plt.colorbar(label='Angle with Z-axis')
    plt.title('Pixel Angles with Z-axis')
    plt.show()


class Camera:
    def __init__(self):
        # get the camera matrix from Matlab
        camera_matrix = np.array([[901.8464, 0, 654.864],
                          [0.0, 901.5054, 362.0497],
                          [0, 0, 1]])
        self.camera_matrix = camera_matrix
        self.fx = camera_matrix[0,0]
        self.fy = camera_matrix[1,1]
        self.cx = camera_matrix[0,2]
        self.cy = camera_matrix[1,2]

        self.image_template = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.angles_map = calculate_angles(self.image_template, self.fx, self.fy, self.cx, self.cy)
    def output(self, pixel):
        x = self.angles_map[pixel[0], pixel[1], 0]
        y = self.angles_map[pixel[0], pixel[1], 1]
        return (x, y)

if __name__ == '__main__':
    camera = Camera()
    visualize_angles(camera.angles_map)