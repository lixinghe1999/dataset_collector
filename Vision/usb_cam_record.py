def video_record(dataset_folder, t=5, plot=True):
    import cv2
    import time
    '''
    Need to plug a USB camera to the computer
    '''
    cap = cv2.VideoCapture(1)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_name = dataset_folder + f'/{str(time.time())}_video.avi'
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(video_name, fourcc, fps, (640, 480))
    frame_idx = 0
    while frame_idx < t * fps:
        ret, frame = cap.read()
        if ret:
            frame_idx += 1
            out.write(frame)
            if plot:
                cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print('Video saved as ', video_name)