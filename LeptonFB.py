#!/usr/bin/python
"""Displays a touchscreen interface for a FLIR Lepton thermal imager on a
Raspberry Pi touchscreen (or any other Kivy compatible device)  """


from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.properties import ObjectProperty
import numpy as np
import cv2
import glob
import time
from pylepton import Lepton
from kivy.core.window import Window

class LeptonFBWidget(Widget):
    """Main class for the Lepton Framebuffer widget"""
    wid = Widget()


    def __init__(self, **kwargs):
        super(LeptonFBWidget, self).__init__(**kwargs)
        # setup a keyboard handler
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.keyboard_handler)
        self.true_range = 0
        self.save_next = 0
        self.last_time = 0
        self.key_action = ""
        self.colourmap = 2

    def _keyboard_closed(self):
        """cleans up keyboard handling on exit"""
        #remove keyboard handler
        self._keyboard.unbind(on_key_down=self.keyboard_handler)
        self._keyboard = None

    def keyboard_handler(self, keyboard, keycode, text, modifiers):
        """called when we press a key"""
        self.key_action = keycode[1]
        return True

    @staticmethod
    def capture(device="/dev/spidev0.0"):
        """capture an image from the Lepton sensor"""
        with Lepton(device) as lepton:
            arr, _ = lepton.capture()
        return arr

    @staticmethod
    def raw_to_temp(value):
        """converts a raw value to a temperature.
        Note: based on a crude approximation, better calibration required.
        Values used here assume startup temp of around 20C"""
        return (value - 7400) / 29


    @staticmethod
    def temp_to_raw(value):
        """converts a temperature to a raw value
        Note: is based on crude approximation, better calibration required.
        Values used here assume startup temp of around 20C"""
        return (value * 29) + 7400


    def draw_image(self):
        """draws everything to the screen"""
        image_rect = ObjectProperty(None)

        texture = Texture.create(size=(80, 60), colorfmt="rgb")
        arr = self.capture(self)

        #uncomment for testing on systems without a Lepton connected
        #arr = np.ndarray(shape=[60, 80, 1], dtype=np.uint8)

        #get the minimum/maximum temp the user wants to display from the slider
        min_temp_show = self.ids["min_temp_slider"].value
        max_temp_show = self.ids["max_temp_slider"].value
        mid_temp_show = ((max_temp_show - min_temp_show) / 2) + min_temp_show

        #don't let them display a min greater than max
        if min_temp_show > max_temp_show:
            min_temp_show = max_temp_show - 1
            self.ids["min_temp_slider"].value = min_temp_show

        #get min, max and centre temperatures from the image
        amin = np.amin(arr)
        amax = np.amax(arr)

        min_temp = self.raw_to_temp(amin)
        max_temp = self.raw_to_temp(amax)

        centre = arr[20][40]
        centre_temp = self.raw_to_temp(centre)

        min_raw_show = self.temp_to_raw(min_temp_show)
        max_raw_show = self.temp_to_raw(max_temp_show)
        raw_show_diff = max_raw_show - min_raw_show

        # clip values between the min and max the user says they want to see
        arr = np.clip(arr, min_raw_show, max_raw_show)
        min_raw = np.amin(arr)
        max_raw = np.amax(arr)

        # normalise image to take 8 bit range
        # temp to force normalisation to use this as max
        # we want to normalise so that min_raw_show to max_raw_show represents
        # an 8 bit range

        diff_divisor = raw_show_diff / 255

        max_raw_norm = (max_raw - min_raw_show) / diff_divisor
        min_raw_norm = (min_raw - min_raw_show) / diff_divisor

        cv2.normalize(arr, arr, min_raw_norm, max_raw_norm, cv2.NORM_MINMAX)

        # create an array 3 elements deep for separate RGB entries
        arr2 = np.ndarray(shape=[60, 80, 3], dtype=np.uint8)

        # convert to array with elements called r,g and b
        dtp = np.dtype(
            (np.uint32, {'r': (np.uint8, 0), 'g': (np.uint8, 1),
                         'b': (np.uint8, 2), 'a': (np.uint8, 3)}))

        # setup labels
        self.ids["status_label"].text = "Lowest Temperature: %d C\n \
        Highest Temperature: %d C\nMiddle Pixel: %d C\nColour Map: %d"\
            % (min_temp, max_temp, centre_temp, self.colourmap)

        self.ids["min_label"].text = "%d C" % (min_temp_show)
        self.ids["mid_label"].text = "%d C" % (mid_temp_show)
        self.ids["max_label"].text = "%d C" % (max_temp_show)

        arr4 = np.uint32(arr)
        for x in range(0, 80):
            for y in range(0, 60):
                #true range = grayscale image with all three channels equal
                if self.true_range == 0:
                    value = 255 - (arr[59 - y][x])

                    arr2[y][x][0] = value
                    arr2[y][x][1] = value
                    arr2[y][x][2] = value
                #if not pull out r,g,b values from value
                else:
                    value = arr4[59 - y][x].view(dtype=dtp)
                    arr2[y][x][0] = value['r']
                    arr2[y][x][1] = value['b']
                    arr2[y][x][2] = value['g']

        #apply the chosen colour map to the image
        arr3 = cv2.applyColorMap(arr2, self.colourmap)

        #save the image
        self.__save_image(arr3, amin, amax, centre, min_temp, max_temp, \
            centre_temp)

        #send image to the screen
        texture.blit_buffer(arr3.tostring(), bufferfmt="ubyte", colorfmt="rgb")

        # redraw and scale to 600x400
        with self.canvas:
            self.image_rect = Rectangle(
                texture=texture, pos=(00, 100), size=(600, 400))

    @staticmethod
    def exit():
        """called when the user presses the exit button"""
        exit(0)

    def change_colourmap(self):
        """called when change colourmap pressed, cycles through colourmaps"""
        self.colourmap = self.colourmap + 1
        if self.colourmap > 11:
            self.colourmap = 0
        self.draw_colourmap()

    @staticmethod
    def change_display():
        """button callback for changing display mode,
        exits with a value of 2 to signal to shell script"""
        #self.change_display_next = 1
        print "changing display"
        exit(1)


    def save_image(self):
        """button call back for saving an image,
        sets a flag to save image next time its captured"""
        self.save_next = 1


    def __save_image(self, arr3, amin, amax, cen, min_temp, max_temp, c_temp):
        """handle saving the image to a file"""
        #convert from RGB to BGR because that's what openCV wants
        bgr = cv2.cvtColor(arr3, cv2.COLOR_RGB2BGR)

        #flip image as its currently backwards to what openCV wants
        out = cv2.flip(bgr, 0)

        #save to a jpg file for streaming over the network
        cv2.imwrite("/tmp/image.jpg", out)

        #see if we are wanting to save this image
        if self.save_next == 1:
            # imwrite wants a BGR not RGB image

            #didn't we just do this?? can old bgr/out be reused?
            bgr = cv2.cvtColor(arr3, cv2.COLOR_RGB2BGR)

            out = cv2.flip(bgr, 0)
            filelist = glob.glob("image*.png")

            maxnum = 0
            #find the highest file number, save the file as that +1
            for filename in filelist:

                filenum = filename.replace("image", "")
                filenum = filenum.replace(".png", "")

                try:
                    if int(filenum) > maxnum:
                        maxnum = int(filenum)
                except ValueError:
                    print "non-integer name %s" % (filename)

            filename = ("image%03d.png") % (maxnum + 1)
            print filename
            #upscale image for better viewing
            out = cv2.resize(out, (320, 240))
            #make a border between image and text area
            out2 = cv2.copyMakeBorder(
                out, 0, 40, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])

            # display text with min, max and centre values
            image_text = "min: %d max: %d centre: %d" % (amin, amax, cen)
            image_text2 = "min: %d max: %d centre: %d" % (
                min_temp, max_temp, c_temp)

            cv2.putText(out2, image_text, (0, 255),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))
            cv2.putText(out2, image_text2, (0, 275),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255))

            #write the file to disk
            cv2.imwrite(filename, out2)

            #add label saying we saved the file if we just hit save
            self.ids["mesg_label"].text = "Saved " + filename
            self.save_next = 0


    def update(self, interval):
        """redraws the image"""

        # restart program if framerate drops
        # due to random bug where kivy scheduler stops running at correct
        # frequency after about 5 min
        if self.last_time == 0:
            self.last_time = time.time()

        time_diff = time.time() - self.last_time

        if time_diff > 1.0:
            print "Large time difference detected, restarting"
            exit(2)
        self.last_time = time.time()

        # check keyboard actions
        #if self.key_action == 'd':
            #self.change_display()
        if self.key_action == 'h':
            exit(0)
        if self.key_action == 's':
            self.save_next = 1
        if self.key_action == 'c':
            self.change_colourmap()
        self.key_action = ''

        self.draw_image()

    def draw_colourmap(self):
        """draw all the colours in the colourmap for the user to see"""
        #colourmap_rect = ObjectProperty(None)

        texture = Texture.create(size=(20, 256), colorfmt="rgb")

        arr = np.ndarray(shape=[256, 20], dtype=np.uint8)
        arr.fill(0)
        for i in range(0, 256):
            for x in range(0, 20):
                arr[i][x] = 255 - i
        arr2 = cv2.applyColorMap(arr, self.colourmap)

        texture.blit_buffer(arr2.tostring(), bufferfmt="ubyte", colorfmt="rgb")

        with self.canvas:
            self.colourmap_rect = Rectangle(
                texture=texture, pos=(780, 100), size=(20, 400))


class LeptonFB(App):
    """"Launcher class, which runs LeptonFBWidget.update at 10hz"""
    def build(self):
        wid = LeptonFBWidget()
        wid.draw_colourmap()
        #draw once every 100 ms
        Clock.schedule_interval(wid.update, 0.1)
        return wid

if __name__ == '__main__':
    LeptonFB().run()
