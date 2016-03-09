from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from functools import partial
import numpy
import cv2
from pylepton import Lepton
 
class CanvasApp(App):
    wid=Widget()
    
    
    def capture(flip_v = False, device = "/dev/spidev0.0"):
        with Lepton(device) as l:
            a,_ = l.capture()
        if flip_v:
            cv2.flip(a,0,a)
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        return np.uint8(a)
    
    
    #function to add rectangle to screen
    def add_rects(self,wid):
    #def add_rects(self):        
        print "in add_rects"
        with wid.canvas:
                Color(1, 0, 0, .5, mode='rgba')
                
                texture = Texture.create(size=(80, 40), colorfmt="rgb")
                arr = self.capture()
                #arr = numpy.random.randint(255,size=(80,40,3))
                #arr = numpy.array([80,40,3],dtype=uint8)
                #arr = numpy.ndarray(shape=[80, 40, 3], dtype=numpy.uint8)
                #arr.fill(127)
                data = arr.tostring()
                texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
                wid.canvas.clear()
                wid.rect = Rectangle(texture=texture, pos=(00,200), size=(640,320))

                #wid.rect = Rectangle(pos=(200,200), size=(300,300))
                 
    #function to clear rectangle from screen
    def reset_rects(self,wid,*largs):
        wid.canvas.clear()
    
    def exit(self,wid,*largs):
        exit(0)
            
    def update(self,t,wid):
        self.add_rects(wid)
 
    def build(self):
        wid = Widget()
          
        #calling function with default arguments
        btn_clear = Button(text='Exit',on_press=partial(self.exit,wid,'Exits the program'))
 
        layout = GridLayout(cols=1,rows=2)
        layout.add_widget(btn_clear)
        root=GridLayout()
        root.add_widget(wid)
        root.add_widget(layout)

        Clock.schedule_interval(partial(self.update,wid=wid), 0.1)
        return root
    
    def __init__(self, **kwargs):
        wid=Widget()
        super(CanvasApp, self).__init__(**kwargs)

 
if __name__ == '__main__':
    CanvasApp().run()
    
    
