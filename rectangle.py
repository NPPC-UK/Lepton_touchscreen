from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from functools import partial
import numpy as np
import cv2
from pylepton import Lepton
 
class LeptonFB(App):
    wid=Widget()

    #capture an image from the Lepton sensor 
    def capture(device = "/dev/spidev0.0"):
        with Lepton(device) as l:
            a,_ = l.capture()
        #flip in x axis as image is backwards if not
        cv2.flip(a,1,a)
        
        #normalise image to take 16 bit range
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        
        #shift so that lower 8 bits contain the most significant bits
        np.right_shift(a, 8, a)

        return np.uint8(np.rot90(a))

    #function to add rectangle to screen
    def draw_image(self,wid):
        with wid.canvas:
                texture = Texture.create(size=(80, 60), colorfmt="rgb")
                arr = self.capture()

        arr2 = np.ndarray(shape=[60,80,3],dtype=np.uint8)
        for x in range(0,80):
            for y in range(0,60):
                arr2[y][79-x][0]=arr[x][y]
                arr2[y][79-x][1]=arr[x][y]
                arr2[y][79-x][2]=arr[x][y]

        data = arr2.tostring() #convert to 8 bit string 
        texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        #clear the screen 
        wid.canvas.clear()
        #redraw and scale to 600x400 
        wid.rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))

    #called when the user presses the exit button
    def exit(self,wid,*largs):
        exit(0)

    #redraws the image
    def update(self,t,wid):
        #grab image and redraw 
        self.draw_image(wid)

    def build(self):
        wid = Widget()

        #calling function with default arguments
        exit_btn = Button(text='Exit',on_press=partial(self.exit,wid,'Exits the program'))

        layout = GridLayout(cols=1,rows=2)
        layout.add_widget(exit_btn)
        root=GridLayout()
        root.add_widget(wid)
        root.add_widget(layout)

        #trigger update to be called every 100ms
        Clock.schedule_interval(partial(self.update,wid=wid), 0.1)
        return root

    def __init__(self, **kwargs):
        wid=Widget()
        super(LeptonFB, self).__init__(**kwargs)

if __name__ == '__main__':
    LeptonFB().run()
