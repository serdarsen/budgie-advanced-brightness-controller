#!/usr/bin/env python3

# Copyright (C) 2016 Ikey Doherty
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# UBrightnessController developed by Serdar ŞEN at 2018 for productivity and fun :)
# https://github.com/serdarsen

# Thanks my references for their projects: 
# budgie-desktop-examples https://github.com/budgie-desktop/budgie-desktop-examples/tree/master/python_project
# LordAmit/Brightness https://github.com/LordAmit/Brightness
# dbrady/bin https://github.com/dbrady/bin/blob/master/indicator-brightness.py
# dgaw/budgie-workspaces-compact https://github.com/dgaw/budgie-workspaces-compact

import gi.repository
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, Gdk
import check_displays as CDisplay
import os, errno

import subprocess
from Log import Log

class UBrightnessController(GObject.GObject, Budgie.Plugin):
    #This is simply an entry point into your Budgie Applet implementation. Note you must always override Object, and implement Plugin.
    
    # Good manners, make sure we have unique name in GObject type system
    __gtype_name__ = "io_serdarsen_github_ubrightnesscontroller"

    def __init__(self):
        #Initialisation is important.
        GObject.Object.__init__(self)

    def do_get_panel_widget(self, uuid):
        #This is where the real fun happens. Return a new Budgie.Applet instance with the given UUID. The UUID is determined by the BudgiePanelManager, and is used for lifetime tracking.
        return UBrightnessControllerApplet(uuid)

class UBrightnessControllerApplet(Budgie.Applet):
    #Budgie.Applet is in fact a Gtk.Bin

    TAG = "UBrightnessControllerApplet"
    manager = None
    isBacklightAvailable = True
    isDimAvailable = True
    dimValue = 0.5
    config_path = ""
    dim_cache_file_path = ""
    image_path = ""
    ubrightnesscontroller_path = ""

    ############################################
    ###  Brightness (Light) methods Start      #
    ############################################
    MAXSTEPS = 15 # Depends on gnome-settings-daemon
    closest = lambda self, num,list: min(list, key = lambda x: abs(x-num))

    def makeDirIfNotExist(self, path):
        if (path is not ""):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    def setBacklightAvailable(self, b):
        self.isBacklightAvailable = b
        if(not self.isBacklightAvailable):
            Log.i(self.TAG, "UBrightnessController No backlight detected")

    def setDimAvailable(self, b):
        self.isDimAvailable = b
        if(not self.isDimAvailable):
            Log.i(self.TAG, "UBrightnessController Dim is not available")

    def get_brightness_settings(self):
        if self.max_brightness < self.MAXSTEPS:
            bs = range(0, self.max_brightness, 1)
        else:
            bs = range(0, self.max_brightness, self.max_brightness//self.MAXSTEPS)
            bs.append(self.max_brightness)
        return bs

    def get_max_brightness(self):
        mb = 0
        try:
            p = subprocess.Popen(['pkexec','/usr/lib/gnome-settings-daemon/gsd-backlight-helper','--get-max-brightness'], stdout=subprocess.PIPE)
            mb = int(p.communicate()[0])
        except:
        
            mb = 0
        return mb

    def get_curr_brightness(self):
        try:
            p = subprocess.Popen(['pkexec','/usr/lib/gnome-settings-daemon/gsd-backlight-helper','--get-brightness'], stdout=subprocess.PIPE)
            self.curr_brightness = int(p.communicate()[0])
            c = self.closest(self.curr_brightness, self.brightness_settings)
        except :
            return self.setBacklightAvailable(False)

        return self.brightness_settings.index(c)

    def setBrightness(self):
        if self.brightnessValue is not None:
            try:
                subprocess.call(['pkexec','/usr/lib/gnome-settings-daemon/gsd-backlight-helper','--set-brightness',"%s" % self.brightnessValue])
            except:
                self.setBacklightAvailable(False)

    # any signal from the scales is signaled to the dimValueLabel the text of which is changed
    def brightness_scale_moved(self, event):
        if(self.isBacklightAvailable):
            self.brightnessValue = "%.0f" % self.brightnessScale.get_value()
            self.setBrightness()
            self.brightnessValueLabel.set_text(self.brightnessValue)

    def initBrightness(self):
        self.max_brightness = self.get_max_brightness()
        self.brightness_settings = self.get_brightness_settings()
        self.brightnessValue = self.get_curr_brightness()

    ############################################
    ###  Brightness (Light) methods End        #
    ############################################

    ############################################
    ###  Brightness (Dim) methods Start        #
    ############################################
    def saveDimValue(self, val):
        if(self.dim_cache_file_path is not ""):
            try:
                file = open(self.dim_cache_file_path, "w+")
                file.write("%s"%(str(val)))
                file.close()
            except:
                Log.e(self.TAG, "error_4010 dim value save error")
        
    def retriveDimValue(self):
        val = "0.5"
        try:
            if (self.dim_cache_file_path is not ""):
                if(os.path.isfile(self.dim_cache_file_path)):
                    file = open(self.dim_cache_file_path, "r+")
                    file.seek(0)
                    val = file.read()
                    file.close()
                    if (val == None):
                        val = "0.5"
                    if (val == ""):
                        val = "0.5"
        except:
            Log.e(self.TAG, "error_4011 dim value retrive error")

        return float("%s"%(val)) 

    def __assign_displays(self):
        #assigns display name

        try:
            self.displays = CDisplay.detect_display_devices()
            self.no_of_displays = len(self.displays)
            self.no_of_connected_dev = self.no_of_displays
            if self.no_of_displays is 1:
                self.display1 = self.displays[0]
            elif self.no_of_displays is 2:
                self.display1 = self.displays[0]
                self.display2 = self.displays[1]        
        except:
            self.setDimAvailable(False)

    def setDim(self):
        #Change brightness
        try:
            cmd_value = "xrandr --output %s --brightness %s" % (self.display1, self.dimValue)
            subprocess.check_output(cmd_value, shell = True)
        except:
            self.setDimAvailable(False)

    # any signal from the scales is signaled to the dimValueLabel the text of which is changed
    def dim_scale_moved(self, event):
        # get brightness from scale ui element
        if(self.isDimAvailable):
            self.dimValue = self.dimScale.get_value() / 100
            self.saveDimValue(self.dimValue)
            self.setDim()
            self.dimValueLabel.set_text("%.1f"%(self.dimValue * 100))

    ############################################
    ###  Brightness (Dim) methods End        #
    ############################################

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)

        # about files
        try:
            self.home_dir = os.path.expanduser("~")
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.ubrightnesscontroller_path = self.home_dir + '/.config/ubrightnesscontroller'
            self.makeDirIfNotExist(self.ubrightnesscontroller_path)
            self.dim_cache_file_path = self.ubrightnesscontroller_path + "/dim.txt"
            self.image_path = self.dir_path + "/brightness.svg"
        except:
            Log.e("error_1015 get files path error")

        #about displays
        self.display1 = None
        self.display2 = None
        self.no_of_connected_dev = 0
        self.__assign_displays()
        self.setDim()
        self.box = Gtk.EventBox()
        
        #about ui
        if(self.image_path is not ""):
            self.iconImage = Gtk.Image()
            self.iconImage.set_from_file(self.image_path)
            #self.iconImage = Gtk.Image.new_from_icon_name("display-brightness-symbolic", Gtk.IconSize.BUTTON)
            self.box.add(self.iconImage)
        self.box.show_all()
        self.add(self.box)
        self.popover = Budgie.Popover.new(self.box)

        #about light
        self.initBrightness();

        if(self.isBacklightAvailable and self.isDimAvailable):
            self.popover.set_default_size(140, 300)
        else:
            self.popover.set_default_size(70, 300)

        if(self.isDimAvailable):
            # Gtk.Adjustment(initial value - won't work properly I'm also using set_value() below, min value, max value, step increment - press cursor keys to see!, page increment - click around the handle to see!, age size - not used here)
            gtkAdjustmentForDimScale = Gtk.Adjustment(50, 10, 100, 5, 0.1, 0) 
        
        if(self.isBacklightAvailable):
            gtkAdjustmentForBrightnessScale = Gtk.Adjustment(2, 0, self.max_brightness, 5, 1, 0)

        if(self.isDimAvailable):
            # a vertical scale
            self.dimScale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=gtkAdjustmentForDimScale)
        
        if(self.isBacklightAvailable):
            self.brightnessScale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=gtkAdjustmentForBrightnessScale)
        
        if(self.isDimAvailable):
            # that can expand vertically if there is space in the grid (see below)
            self.dimScale.set_value_pos(Gtk.PositionType.BOTTOM)    
            self.dimScale.set_draw_value (False)
            self.dimScale.set_vexpand(True)
            self.dimScale.set_hexpand(True)
            self.dimScale.set_inverted(True)

        if(self.isBacklightAvailable):
            self.brightnessScale.set_value_pos(Gtk.PositionType.BOTTOM)
            self.brightnessScale.set_draw_value (False)
            self.brightnessScale.set_vexpand(True)
            self.brightnessScale.set_hexpand(True)
            self.brightnessScale.set_inverted(True)
        
        if(self.isDimAvailable):
            # we connect the signal "value-changed" emitted by the scale with the callback function scale_moved
            self.dimScale.connect("value-changed", self.dim_scale_moved)
        
        if(self.isBacklightAvailable):
            self.brightnessScale.connect("value-changed", self.brightness_scale_moved)

        if(self.isDimAvailable):
            # value labels
            self.dimValueLabel = Gtk.Label()
            self.dimValueLabel.set_text("")
       
        if(self.isBacklightAvailable):
            self.brightnessValueLabel = Gtk.Label()
            self.brightnessValueLabel.set_text("")

        if(self.isDimAvailable):
            self.dimTitleLabel = Gtk.Label()
            self.dimTitleLabel.set_text("Dim")

        if(self.isBacklightAvailable):
            self.brightnessTitleLabel = Gtk.Label()
            self.brightnessTitleLabel.set_text("Light")

        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_column_homogeneous(True)
        grid.set_margin_top(5)
        grid.set_margin_bottom(5)
        grid.set_margin_left(5)
        grid.set_margin_right(5)

        if(self.isBacklightAvailable and self.isDimAvailable):
            #Brightness
            grid.attach(self.brightnessTitleLabel, 0, 0, 1, 1)
            grid.attach(self.brightnessScale, 0, 1, 1, 1)
            grid.attach(self.brightnessValueLabel, 0, 2, 1, 1)

            #Dim
            grid.attach(self.dimTitleLabel, 1, 0, 1, 1)
            grid.attach(self.dimScale, 1, 1, 1, 1)
            grid.attach(self.dimValueLabel, 1, 2, 1, 1)

        elif(self.isDimAvailable):
            #Dim
            grid.attach(self.dimTitleLabel, 0, 0, 1, 1)
            grid.attach(self.dimScale, 0, 1, 1, 1)
            grid.attach(self.dimValueLabel, 0, 2, 1, 1)

        elif(self.isBacklightAvailable):
            #Brightness
            grid.attach(self.brightnessTitleLabel, 0, 0, 1, 1)
            grid.attach(self.brightnessScale, 0, 1, 1, 1)
            grid.attach(self.brightnessValueLabel, 0, 2, 1, 1)

        self.popover.add(grid)
        self.popover.get_child().show_all()
        self.box.show_all()
        self.show_all()
        self.box.connect("button-press-event", self.on_press)
        
        if(self.isDimAvailable):
            self.dimValue = self.retriveDimValue()
            self.dimScale.set_value(self.dimValue * 100)

        if(self.isBacklightAvailable):
            self.setBrightness()
            self.brightnessScale.set_value(self.brightnessValue)

    def on_press(self, box, e):
        if e.button != 1:
            return Gdk.EVENT_PROPAGATE
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.manager.show_popover(self.box)
        return Gdk.EVENT_STOP

    def do_update_popovers(self, manager):
        self.manager = manager
        self.manager.register_popover(self.box, self.popover)
