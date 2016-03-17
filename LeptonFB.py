#!/usr/bin/python

from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.clock import Clock
from functools import partial
import numpy as np
import cv2
import colorsys
from pylepton import Lepton
 
class LeptonFB(App):
    wid=Widget()
    true_range=0
    save_next=0

    l = Label(text="Normalised",pos=(200,00))
    status_label = Label(pos=(400,0))
    

    #capture an image from the Lepton sensor 
    def capture(self,flip_v = False , device = "/dev/spidev0.0"):

        with Lepton(device) as l:
            a,_ = l.capture()
        
	if self.true_range == 0:
    	    #normalise image to take 16 bit range
    	    cv2.normalize(a, a, 0, 255, cv2.NORM_MINMAX)

            #shift so that lower 8 bits contain the most significant bits
    	    #np.right_shift(a, 8, a)
	#else:
	    #a2=cv2.applyColorMap(a,cv2.COLORMAP_OCEAN)
	    #a=np.reshape(a2,(60,80,1))
	
        return np.uint32(a)

    def rgb(self,minval,maxval,val,minangle,anglerange):
	#s = (float(v-minval) / (maxval-minval)) * anglerange
	v = (float(val-minval) / (maxval-minval)) * (anglerange/3)
	v = v + 100
	#h = 240
	h = (float(val-minval) / (maxval-minval)) * (anglerange)
	h = h + minangle
	
	r,g,b = colorsys.hsv_to_rgb(h/360,1.0,v/360)
	return int(r*255),int(g*255),int(b*255)
	#return v,v,v
    
    def colourMap(self,value):
	aR = 0
	aG = 0
	aB = 255
	bR = 255
	bG = 0
	bB = 0
	
	r = (float)(bR - aR) * value + aR
	g = (float)(bG - aG) * value + aG
	b = (float)(bB - bB) * value + aB

	return (r,g,b)

    #function to add rectangle to screen
    def draw_image(self,wid):
        with wid.canvas:
    	    texture = Texture.create(size=(80, 60), colorfmt="rgb")
            arr = self.capture(self)
    	    arr2 = np.ndarray(shape=[60,80,3],dtype=np.uint8)
	    #dt=np.dtype((np.uint32,{'r':(np.uint8,0),'g':(np.uint8,1),'b':(np.uint8,2),'a':(np.uint8,3)}))
	    amin=np.amin(arr)
	    amax=np.amax(arr)
	    self.status_label.text = "range: %d min: %d max: %d" % (amax-amin,amin,amax)
    	    for x in range(0,80):
        	for y in range(0,60):
		    #v = arr[59-y][x].view(dtype=dt)
		    if self.true_range == 0:
			value = arr[59-y][x]
			
			#print "value=%d" % (value)		
			r,g,b = self.rgb(0,255,value,240,120)
			#print "r=%d g=%d b=%d" % (r,g,b)
			

			arr2[y][x][0]=r
			arr2[y][x][1]=g
            		arr2[y][x][2]=b
		    else: 
			value = arr[59-y][x]
			#print value

			#10000 approx 100C 8000 approx 20C, 7500 approx 0??
			#r,g,b = self.rgb(7500,8800,value,160,200)
			r,g,b = self.colourMap(value)
			#print r
			#print g
			#print b
			arr2[y][x][0]=r
			arr2[y][x][1]=g
            		arr2[y][x][2]=b

	    #print arr[30][40].view(dtype=dt)['r']
	    #print arr[30][40].view(dtype=dt)['g']
	    #print arr[30][40].view(dtype=dt)['b']

    	    data = arr2.tostring() #convert to 8 bit string 

	    #see if we are wanting to save this image
	    if self.save_next == 1:
		#imwrite wants a BGR not RGB image
		bgr = cv2.cvtColor(arr2,cv2.COLOR_RGB2BGR)
		
    		cv2.imwrite("image.png",bgr)
		self.save_next=0

    	    texture.blit_buffer(data, bufferfmt="ubyte", colorfmt="rgb")
        
	    #clear the screen 
    	    wid.canvas.clear()
    	    #redraw and scale to 600x400 
    	    wid.rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))

    #called when the user presses the exit button
    def exit(self,wid,*largs):
        exit(0)

    #called when the user presses the exit button
    def change_mode(self,wid,*largs):
        if self.true_range == 0:
	    self.true_range = 1
	    self.l.text="True Range"
	else:
	    self.true_range = 0
	    self.l.text="Normalised"
	print "changed mode"

    def save_image(self,wid,*largs):
	self.save_next=1

    #redraws the image
    def update(self,t,wid):
        #grab image and redraw 
        self.draw_image(wid)

    def draw_colourmap(self,wid):
	for i in range(7500,8500,2):
	    c = Color(colourMap(i))

	    Line(points=[500,(i/2)-7500,500,(i/2)-7499],width=1)
	    

    def build(self):
        wid = Widget()

        #calling function with default arguments
        exit_btn = Button(pos=(0,00),text='Exit',on_press=partial(self.exit,wid,'Exits the program'))
        mode_btn = Button(pos=(100,00),text='Change Mode',on_press=partial(self.change_mode,wid,'Changes Image Mode'))
	save_btn = Button(pos=(200,0),text='Save',on_press=partial(self.save_image,wid,'Saves the current view'))

	red_slider = Slider(pos=(600,300),height=200,min=0,max=255,value=128,orientation='vertical')
	green_slider = Slider(pos=(650,300),height=200,min=0,max=255,value=128,orientation='vertical')
	blue_slider = Slider(pos=(700,300),height=200,min=0,max=255,value=128,orientation='vertical')
	red2_slider = Slider(pos=(600,00),height=200,min=0,max=255,value=128,orientation='vertical')
	green2_slider = Slider(pos=(650,00),height=200,min=0,max=255,value=128,orientation='vertical')
	blue2_slider = Slider(pos=(700,00),height=200,min=0,max=255,value=128,orientation='vertical')
	
        root=GridLayout()
        root.add_widget(wid)

        #layout = GridLayout(cols=4,row_default_height=20,spacing=[2,2])
	root.add_widget(self.l)
	root.add_widget(self.status_label)
        root.add_widget(exit_btn)
        root.add_widget(mode_btn)
	root.add_widget(save_btn)
        root.add_widget(red_slider)
        root.add_widget(red2_slider)
        root.add_widget(green_slider)
        root.add_widget(green2_slider)
        root.add_widget(blue_slider)
        root.add_widget(blue2_slider)

        #trigger update to be called every 100ms
        Clock.schedule_interval(partial(self.update,wid=wid), 0.1)
        return root

    def __init__(self, **kwargs):
        wid=Widget()
        super(LeptonFB, self).__init__(**kwargs)

if __name__ == '__main__':
    LeptonFB().run()
