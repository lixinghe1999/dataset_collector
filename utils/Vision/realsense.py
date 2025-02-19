## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2
import datetime
import matplotlib.pyplot as plt

def tof_stream():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()

    # Get device product line for setting a supporting resolution
    pipeline_wrapper = rs.pipeline_wrapper(pipeline)
    pipeline_profile = config.resolve(pipeline_wrapper)
    device = pipeline_profile.get_device()
    device_product_line = str(device.get_info(rs.camera_info.product_line))

    found_rgb = False
    for s in device.sensors:
        if s.get_info(rs.camera_info.name) == 'RGB Camera':
            found_rgb = True
            break
    if not found_rgb:
        print("The demo requires Depth camera with Color sensor")
        exit(0)

    config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

    # Start streaming
    datetime_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S.%f")
    # if file is not None:
    config.enable_record_to_file("dataset/tof/" + datetime_str + ".bag")
    profile = pipeline.start(config)
    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()

    try:
        # use ESC to exit the loop
        while True:
            # Wait for a coherent pair of frames: depth and color
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Convert images to numpy arrays
            depth_image = np.asanyarray(depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
            depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
            #depth_colormap = depth_image * depth_scale
            # repeat the depth image 3 times to make it 3 channel
            # depth_colormap = cv2.cvtColor(depth_colormap, cv2.COLOR_GRAY2BGR)

            depth_colormap_dim = depth_colormap.shape
            color_colormap_dim = color_image.shape

            # If depth and color resolutions are different, resize color image to match depth image for display
            if depth_colormap_dim != color_colormap_dim:
                resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
                images = np.hstack((resized_color_image, depth_colormap))
            else:
                # images = depth_colormap
                images = np.hstack((color_image, depth_colormap))
            # Show images
            # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('RealSense', images)
            if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII value for ESC
                break
    finally:
        # Stop streaming
        pipeline.stop()

def tof_load(file):
  # Setup:
    pipe = rs.pipeline()
    cfg = rs.config()
    cfg.enable_device_from_file(file)
    profile = pipe.start(cfg)
    depth_scale = profile.get_device().first_depth_sensor().get_depth_scale()
    # Skip 5 first frames to give the Auto-Exposure time to adjust
    for x in range(5):
        pipe.wait_for_frames()
    return pipe, depth_scale

def face_depth(frameset, bbox, depth_scale):
    depth = np.asanyarray(frameset.get_depth_frame().get_data())
    face_depth = []
    for i in range(bbox.shape[0]):
        _bbox = bbox[i, :] # [x1, y1, x2, y2]
        _bbox = [int(_bbox[0] * depth.shape[1]), int(_bbox[1] * depth.shape[0]), int(_bbox[2] * depth.shape[1]), int(_bbox[3] * depth.shape[0])]

        depth_crop = depth[_bbox[1]:_bbox[3], _bbox[0]:_bbox[2]].astype(float) * depth_scale
        depth_mean = depth_crop.mean()
        face_depth.append(depth_mean)
    face_depth = np.array(face_depth)
    return face_depth

def show_frame(frameset,):
    color_frame = frameset.get_color_frame()
      
    color = np.asanyarray(color_frame.get_data())

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
    # show 0.1 second
    plt.pause(0.1)

def show_output(frameset, bbox, face_depths, normal_vecs):
    color_frame = frameset.get_color_frame()
    images = np.asanyarray(color_frame.get_data())
    print(images.shape, bbox.shape, face_depths.shape, normal_vecs.shape)

    # Show the two frames together:
    plt.rcParams["axes.grid"] = False
    plt.rcParams['figure.figsize'] = [6, 6]
    plt.imshow(images)

    for box, face_depth, normal_vec in zip(bbox, face_depths, normal_vecs):
        print(box, face_depth, normal_vec)
        x1, y1, x2, y2 = box
        x1, y1, x2, y2 = int(x1 * images.shape[1]), int(y1 * images.shape[0]), int(x2 * images.shape[1]), int(y2 * images.shape[0])
        plt.plot([x1, x2, x2, x1, x1], [y1, y1, y2, y2, y1], 'r-')
        plt.text(x1, y1, f"{face_depth:.2f}", color='red')

        # convert to [x, y, z] vector into azimuth and elevation
        azimuth = np.arctan2(normal_vec[2], normal_vec[0])
        plt.title(f"Azimuth: {np.degrees(azimuth):.2f}, ")
    plt.pause(0.1)
    plt.cla()
    # plt.show()