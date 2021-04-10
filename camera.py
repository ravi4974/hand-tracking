import cv2

class WebCamera:
    def __init__(self,video_capture_index=0,flip=False):
        self.cap = cv2.VideoCapture(0)
        self.flip=flip
    
    def get_dimension(self):
        return (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH),self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def get_frames(self,callback,show_window=False):
        if not callable(callback):
            raise TypeError("callback is not callable")

        while True:
            success, img = self.cap.read()
            if self.flip:
                img=cv2.flip(img,1)

            callback(img)

            if show_window:
                cv2.imshow("image", img)
                cv2.waitKey(1)

if __name__=='__main__':
    cam=WebCamera()

    def process_frames(img):
        pass

    cam.get_frames(process_frames,show_window=True)