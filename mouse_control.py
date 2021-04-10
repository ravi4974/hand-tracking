import win32api,win32con,math
import numpy as np
from camera import Camera
from hand_tracking import HandDetector

class MouseControl:
    def __init__(self):
        self.cam=Camera(flip=True)
        self.detector=HandDetector(num_hands=1)
        self.screen_width=win32api.GetSystemMetrics(78)
        self.screen_height=win32api.GetSystemMetrics(79)

        self.img_width=None
        self.img_height=None
        self.viewport_offset_pct=0.1

        self.__values={}
    
    def __get_distance(self,point_1,point_2):
        _,x1,y1,z1=point_1
        _,x2,y2,z2=point_2

        return int(math.hypot(x2-x1,y2-y1,z2-z1))
    
    def __set_viewport_values(self,img):
        if not self.img_width and not self.img_height:
            self.img_height,self.img_width,_=img.shape
            
            self.viewport_start_x=self.viewport_offset_pct*self.img_width
            self.viewport_end_x=self.img_width-self.viewport_start_x

            self.viewport_start_y=self.viewport_offset_pct*self.img_height
            self.viewport_end_y=self.img_height-self.viewport_start_y

            print(self.viewport_start_x,self.viewport_start_y,self.viewport_end_x,self.viewport_end_y)

    def __set_position(self):
        _,x,y,z=self.result[HandDetector.codes.MIDDLE_FINGER_MCP]

        
        # cx=int(np.interp(x,[xs,xe],[0,xe//2]))
        # cy=int(np.interp(y,[ys,ye],[0,ye//2]))

        # cx=int(np.interp(cx,[0,xe//2],[0,self.screen_width]))
        # cy=int(np.interp(cy,[0,ye//2],[0,self.screen_height]))
        
        cx=int(np.interp(x,[self.viewport_start_x,self.viewport_end_x],[0,self.screen_width]))
        cy=int(np.interp(y,[self.viewport_start_y,self.viewport_end_y],[0,self.screen_height]))

        #smooth the value
        pcx=self.__values.get('PREV_CX',0)
        pcy=self.__values.get('PREV_CY',0)
        
        index_mcp=self.result[HandDetector.codes.INDEX_FINGER_MCP]
        middle_mcp=self.result[HandDetector.codes.MIDDLE_FINGER_MCP]

        if self.__get_distance([0,cx,cy,0],[0,pcx,pcy,0])>self.__get_distance(index_mcp,middle_mcp)*0.1:
            win32api.SetCursorPos((cx,cy))
            self.__values['PREV_CX']=cx
            self.__values['PREV_CY']=cy
    
    def __left_click(self):
        index_tip=self.result[HandDetector.codes.INDEX_FINGER_TIP]
        thumb_tip=self.result[HandDetector.codes.THUMB_TIP]

        index_mcp=self.result[HandDetector.codes.INDEX_FINGER_MCP]
        middle_mcp=self.result[HandDetector.codes.MIDDLE_FINGER_MCP]

        tip_distance=self.__get_distance(thumb_tip,index_tip)
        mcp_distance=self.__get_distance(index_mcp,middle_mcp)

        LEFT_CLICKED=self.__values.get('LEFT_CLICKED',False)

        if tip_distance<mcp_distance*0.8 and not LEFT_CLICKED and index_tip[2]<thumb_tip[2]:
            self.__values['LEFT_CLICKED']=True
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        elif tip_distance>mcp_distance*2 and LEFT_CLICKED:
            self.__values['LEFT_CLICKED']=False
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    
    def __scroll(self):
        middle_mcp=self.result[HandDetector.codes.MIDDLE_FINGER_MCP]
        z=middle_mcp[3]

        scroll_value=int(np.interp(z,[-15,15],[-30,40]))

        if abs(scroll_value)<20:
            scroll_value=0
        
        # print(scroll_value)

        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,scroll_value,0)

    def __reset(self):
        self.__values={}
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

    def process_frames(self,img):
        self.__set_viewport_values(img)

        self.result=self.detector.get_hand_coordinates(img,hand="Right")
        if len(self.result):
            self.__set_position()
            self.__left_click()
            self.__scroll()
        else:
            self.__reset()
    
    def start(self):
        self.__reset()
        self.cam.get_frames(self.process_frames,True)


if __name__=='__main__':
    mouse_control=MouseControl()
    mouse_control.start()