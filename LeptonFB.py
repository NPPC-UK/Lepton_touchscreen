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
from kivy.lang import Builder 
from functools import partial
from kivy.properties import NumericProperty, ReferenceListProperty,ObjectProperty
import numpy as np
import cv2
import colorsys
import glob
import time
from pylepton import Lepton
from random import randint
from kivy.core.window import Window
from kivy.modules import keybinding

class LeptonFBWidget(Widget):
    wid=Widget()
    true_range=0
    save_next=0
    last_time=0
    key_action=""

    def __init__(self,**kwargs):
	super(LeptonFBWidget,self).__init__(**kwargs)
	self._keyboard = Window.request_keyboard(self._keyboard_closed,self)
	self._keyboard.bind(on_key_down=self.keyboard_handler)

    def _keyboard_closed(self):
	print "Keyboard closed"
	self._keyboard.unbind(on_key_down=self.keyboard_handler)
	self._keyboard=None

    def keyboard_handler(self,keyboard,keycode,text,modifiers):
	self.key_action=keycode[1]
	return True


    #capture an image from the Lepton sensor 
    def capture(self,flip_v = False , device = "/dev/spidev0.0"):
	#print "waiting for capture " + str(time.time())
        with Lepton(device) as l:
            a,_ = l.capture()
	#print "capture done " + str(time.time())
	#print a.shape
        return a

    def rgb(self,minval,maxval,val,minangle,anglerange):
        #s = (float(v-minval) / (maxval-minval)) * anglerange
        v = (float(val-minval) / (maxval-minval)) * (anglerange/3)
        v =  v + 100
        #h = 240
        h = (float(val-minval) / (maxval-minval)) * (anglerange)
        h =  h + minangle
        
        r,g,b = colorsys.hsv_to_rgb(h/360,1.0,v/360)
        return int(r*255),int(g*255),int(b*255)
        #return v,v,v
    
    def colourMap(self,value,aR,aG,aB,bR,bG,bB):
        
        r = (float)(bR - aR) * value + aR
        g = (float)(bG - aG) * value + aG
        b = (float)(bB - bB) * value + aB

        return (r,g,b)
    
    def convertTemp(self,value):
	return (value-7600)/29

    #function to add rectangle to screen
    def draw_image(self,dt):
        image_rect = ObjectProperty(None)

	    

        texture = Texture.create(size=(80, 60), colorfmt="rgb")
        arr = self.capture(self)
	#print "captured image shape"
	#print arr.shape

        amin=np.amin(arr)
        amax=np.amax(arr)
	centre=arr[20][40]
	min_temp=self.convertTemp(amin)
	max_temp=self.convertTemp(amax)
	cen_temp=self.convertTemp(centre)
	#print "converted temp " + str(time.time())

        if self.true_range == 0:
	    arr = arr-7500
            #normalise image to take 16 bit range
            cv2.normalize(arr, arr, 0, 255, cv2.NORM_MINMAX)
	    #print "normalisation complete " + str(time.time())

            #shift so that lower 8 bits contain the most significant bits
            #np.right_shift(arr, 8, arr)
        #a = np.ndarray(shape=[60,80],dtype=np.uint32)
        #a.fill(randint(7500,8500))
        
        #else:
        #a2=cv2.applyColorMap(a,cv2.COLORMAP_OCEAN)
        #a=
    
        #return np.uint32(a)


        arr2 = np.ndarray(shape=[60,80,3],dtype=np.uint8)
	#print "reshaped array " + str(time.time())

        dtp=np.dtype((np.uint32,{'r':(np.uint8,0),'g':(np.uint8,1),'b':(np.uint8,2),'a':(np.uint8,3)}))
        self.ids["status_label"].text = "fps: %f\nrange: %d\nmin: %d\nmax: %d centre: %d" % (1/dt,amax-amin,amin,amax,centre)
	self.ids["min_label"].text="Min: %d C" % (min_temp)
	self.ids["mid_label"].text="Mid: %d C" % (cen_temp)
	self.ids["max_label"].text="Max: %d C" % (max_temp)
	#print "drawn labels " + str(time.time())

        #aR = int(self.ids["red_slider"].value)
        #aG = int(self.ids["green_slider"].value)
        #aB = int(self.ids["blue_slider"].value)
        #bR = int(self.ids["red2_slider"].value)
        #bG = int(self.ids["green2_slider"].value)
        #bB = int(self.ids["blue2_slider"].value)
	#hsv = np.ndarray(shape=[60,80])
	#print "pre color map"
	#print arr.shape
	#np.reshape(arr,(60,80))

	#print "post color map" 
	#print arr.shape
        a=np.uint32(arr)
        for x in range(0,80):
            for y in range(0,60):
                #v = arr[59-y][x].view(dtype=dt)
                if self.true_range == 0:
                    value = 255-(arr[59-y][x])
            
                    arr2[y][x][0]=value
                    arr2[y][x][1]=value
                    arr2[y][x][2]=value
                else: 
		    #print "value = %d" % (arr[59-y][x])
		    #print a.shape
		    #print "x = %d y= %d" % (x,59-y)
                    value = a[59-y][x].view(dtype=dtp)


                    #10000 approx 100C 8000 approx 20C, 7500 approx 0??
                    #r,g,b = self.rgb(7500,8800,value,160,200)

                    #r,g,b = self.colourMap(value,aR,aG,aB,bR,bG,bB)
                    #print r
                    #print g
                    #print b
                    arr2[y][x][0]=value['r']
                    arr2[y][x][1]=value['b']
                    arr2[y][x][2]=value['g']
	
        #print "parsed array " + str(time.time())

        arr3 = cv2.applyColorMap(arr2,7)
        #print "applied colourmap " + str(time.time())

        bgr = cv2.cvtColor(arr3,cv2.COLOR_RGB2BGR)
        #print "converted colourspace " + str(time.time())

        out = cv2.flip(bgr,0)
        #print "flipped image " + str(time.time())

        cv2.imwrite("/tmp/image.jpg",out)
        #print "written image " + str(time.time())

        #see if we are wanting to save this image
        if self.save_next == 1:
            #imwrite wants a BGR not RGB image
            bgr = cv2.cvtColor(arr3,cv2.COLOR_RGB2BGR)
	    out = cv2.flip(bgr,0)
	    filelist = glob.glob("image*.png")
	    
	    maxnum=0
	    for filename in filelist:
		
		filenum=filename.replace("image","")
		filenum=filenum.replace(".png","")
		
		try:
		    if int(filenum) > maxnum:
			maxnum = int(filenum)
		except ValueError:
		    print "non-integer name %s" % (filename)
	    
	    filename=("image%03d.png") % (maxnum+1)
	    print filename
	    out = cv2.resize(out,(320,240))
	    out2 = cv2.copyMakeBorder(out,0,40,0,0,cv2.BORDER_CONSTANT,value=[0,0,0])
	    imageText="min: %d max: %d centre: %d" % (amin,amax,centre)
	    imageText2="min: %d max: %d centre: %d" % (min_temp,max_temp,cen_temp)

	    #cv2.InitFont(cv.CV_FONT_HERSHEY_PLAIN,1,1,shear=0,thickness=1,lineType=8)
	    cv2.putText(out2,imageText,(0,255),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255))
	    cv2.putText(out2,imageText2,(0,275),cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255))
            cv2.imwrite(filename,out2)
	    
            self.ids["mesg_label"].text="Saved "+filename
            self.save_next=0

        texture.blit_buffer(arr3.tostring(), bufferfmt="ubyte", colorfmt="rgb")
        #print "blitted texture " + str(time.time())
        
        #clear the screen 
        #wid.canvas.clear()
        #redraw and scale to 600x400 
        with self.canvas:
            self.image_rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))
	
        #print "drawn image " + str(time.time())
        #wid.rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))

    #called when the user presses the exit button
    def exit(self):
        exit(0)

    #called when the user presses the exit button
    def change_mode(self):
        if self.true_range == 0:
            self.true_range = 1
            self.ids["mode_label"].text="Mode: True Range"
        else:
            self.true_range = 0
            self.ids["mode_label"].text="Mode: Normalised"
        print "changed mode"

    def change_display(self):
	self.change_display_next=1
	print "changing display"
	exit(1)

    def save_image(self):
        self.save_next=1

    #redraws the image
    def update(self,t):

	#restart program if framerate drops
	# due to random bug where kivy scheduler stops running at right frequency after about 5 min
	if self.last_time==0:
	    self.last_time=time.time()

	time_diff=time.time()-self.last_time

	if time_diff>1.0:
	    print "Large time difference detected, restarting"
	    exit(2)
	self.last_time=time.time()

	#check keyboard actions
	if self.key_action == 'd':
	    self.change_display()
	if self.key_action == 'h':
	    exit(0)
	if self.key_action == 's':
	    self.save_next=1
	if self.key_action == 'm':
	    self.change_mode()
        self.key_action = ''


	#print "starting update" + str(time.time())
	#print "time diff = " + str(time_diff)
        #grab image and redraw 
        self.draw_image(t)
	#print "update complete" + str(time.time())
	#print


    def draw_colourmap(self):
        colourmap_rect = ObjectProperty(None)
              
        t = Texture.create(size=(20, 256), colorfmt="rgb")

	arr = np.ndarray(shape=[256,20],dtype=np.uint8)
	arr.fill(0)
        for i in range(0,256):
	    for x in range(0,20):
		arr[i][x]=255-i
    	arr2 = cv2.applyColorMap(arr,7)

        t.blit_buffer(arr2.tostring(), bufferfmt="ubyte", colorfmt="rgb")

        with self.canvas:
            self.colourmap_rect = Rectangle(texture=t,pos=(780,100),size=(20,400))
	    #pos=(650,150)


class LeptonFB(App):

    def build(self):
        wid = LeptonFBWidget()
	wid.draw_colourmap()
        Clock.schedule_interval(wid.update, 0.1)
        return wid

if __name__ == '__main__':
    LeptonFB().run()
