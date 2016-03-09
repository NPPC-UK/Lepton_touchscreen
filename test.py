import kivy
import numpy
kivy.require('1.0.6') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle

class MyApp(App):

    def build(self):
        
        parent = Widget()
        
        def do_something(obj):
            print "button pressed"
            
        button = Button(text='Hello World')
        parent.add_widget(button)
        button.bind(on_press=do_something)
        
        
        texture = Texture.create(size=(16, 16), colorfmt="rgb")
        #arr = numpy.ndarray(shape=[16, 16, 3], dtype=numpy.uint8)
        arr = numpy.random.randint(255,size=(16,16))
        # fill your numpy array here
        data = arr.tostring()
        texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        self.canvas.add(Rectangle(texture=texture, pos=(0, 0), size=(16, 16)))

        
        return parent

if __name__ == '__main__':
    MyApp().run()
