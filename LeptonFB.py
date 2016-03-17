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
from pylepton import Lepton
from random import randint


class LeptonFBWidget(Widget):
    wid=Widget()
    true_range=0
    save_next=0

    #capture an image from the Lepton sensor 
    def capture(self,flip_v = False , device = "/dev/spidev0.0"):

        #with Lepton(device) as l:
        #    a,_ = l.capture()
        a = np.ndarray(shape=[60,80],dtype=np.uint32)
        a.fill(randint(7500,8500))
        
        #if self.true_range == 0:
            #normalise image to take 16 bit range
            #cv2.normalize(a, a, 0, 255, cv2.NORM_MINMAX)

            #shift so that lower 8 bits contain the most significant bits
            #np.right_shift(a, 8, a)
        #else:
        #a2=cv2.applyColorMap(a,cv2.COLORMAP_OCEAN)
        #a=np.reshape(a2,(60,80,1))
    
        #return np.uint32(a)
        return a

    def rgb(self,minval,maxval,val,minangle,anglerange):
        #s = (float(v-minval) / (maxval-minval)) * anglerange
        v = (float(val-minval) / (maxval-minval)) * (anglerange/3)
        v =  100
        #h = 240
        h = (float(val-minval) / (maxval-minval)) * (anglerange)
        h =  minangle
        
        r,g,b = colorsys.hsv_to_rgb(h/360,1.0,v/360)
        return int(r*255),int(g*255),int(b*255)
        #return v,v,v
    
    def colourMap(self,value):
        aR = int(self.ids["red_slider"].value)
        aG = int(self.ids["green_slider"].value)
        aB = int(self.ids["blue_slider"].value)
        bR = int(self.ids["red2_slider"].value)
        bG = int(self.ids["green2_slider"].value)
        bB = int(self.ids["blue2_slider"].value)
        
        r = (float)(bR - aR) * value + aR
        g = (float)(bG - aG) * value + aG
        b = (float)(bB - bB) * value + aB

        return (r,g,b)

    #function to add rectangle to screen
    def draw_image(self):
        image_rect = ObjectProperty(None)
              
        texture = Texture.create(size=(80, 60), colorfmt="rgb")
        arr = self.capture(self)
        print arr.shape
        arr2 = np.ndarray(shape=[60,80,3],dtype=np.uint8)

        #dt=np.dtype((np.uint32,{'r':(np.uint8,0),'g':(np.uint8,1),'b':(np.uint8,2),'a':(np.uint8,3)}))
        amin=np.amin(arr)
        amax=np.amax(arr)
        self.ids["status_label"].text = "range: %d\nmin: %d\nmax: %d" % (amax-amin,amin,amax)
        for x in range(0,80):
            for y in range(0,60):
                #v = arr[59-y][x].view(dtype=dt)
                if self.true_range == 0:
                    value = arr[59-y][x]
            
                    print "value=%d" % (value)     
                    r,g,b = self.colourMap(value)
                    #r,g,b = self.rgb(0,255,value,240,120)
                    #r = value[0]
                    #g = value[1]
                    #b = value[2]
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
        #wid.canvas.clear()
        #redraw and scale to 600x400 
        with self.canvas:
            self.image_rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))

        #wid.rect = Rectangle(texture=texture, pos=(00,100), size=(600,400))

    #called when the user presses the exit button
    def exit(self,wid,*largs):
        exit(0)

    #called when the user presses the exit button
    def change_mode(self):
        if self.true_range == 0:
            self.true_range = 1
            self.ids["mode_label"].text="True Range"
        else:
            self.true_range = 0
            self.ids["mode_label"].text="Normalised"
        print "changed mode"

    def save_image(self):
        self.save_next=1

    #redraws the image
    def update(self,t):
        #grab image and redraw 
        self.draw_image()

    def draw_colourmap(self,wid):
        for i in range(7500,8500,2):
            c = Color(colourMap(i))
            Line(points=[500,(i/2)-7500,500,(i/2)-7499],width=1)           

class LeptonFB(App):
     def build(self):
        wid = LeptonFBWidget()
        Clock.schedule_interval(wid.update, 0.1)
        return wid

if __name__ == '__main__':
    LeptonFB().run()
