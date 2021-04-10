import cv2
import mediapipe as mp
from camera import Camera

class HandDetector:
    codes=mp.solutions.hands.HandLandmark

    def __init__(self, static_mode=False, num_hands=2, detection_confidence=0.5, tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        self.hands = self.mp_hands.Hands(static_image_mode=static_mode, max_num_hands=num_hands,
                                         min_detection_confidence=detection_confidence, min_tracking_confidence=tracking_confidence)
        
    def find_hands(self,img,draw=True):
        img.flags.writeable=False
        self.result=self.hands.process(img)
        self.landmarks=self.result.multi_hand_landmarks


        if self.landmarks and draw:
            img.flags.writeable=True
            for hand_landmarks in self.landmarks:
                self.mp_drawing.draw_landmarks(img,hand_landmarks,self.mp_hands.HAND_CONNECTIONS)
        return img
    
    def get_hand_coordinates(self,img,hand=None,draw=True):
        coors=[]

        self.find_hands(img,draw=draw)
        
        if self.landmarks:
            
            for idx,hand_landmark in enumerate(self.landmarks):
                if hand and self.result.multi_handedness[idx].classification[0].label.lower() != hand.lower():
                    continue

                for id,coor in enumerate(hand_landmark.landmark):
                    im_h,im_w,_=img.shape

                    x,y,z=coor.x*im_w,coor.y*im_h,coor.z*100
                    coors.append([id,x,y,z])

                    if draw:
                        img.flags.writeable=True
                        cv2.circle(img,(int(x),int(y)),10,(255,0,255),cv2.FILLED)

        return coors

    

def main():
    cam=Camera()
    detector=HandDetector()
    
    def process_frames(img):
        imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        detector.get_hand_coordinates(img)
    
    cam.get_frames(process_frames,True)


if __name__ == '__main__':
    main()
