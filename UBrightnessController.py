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


import gi.repository
gi.require_version('Budgie', '1.0')
gi.require_version('Wnck', '3.0')
from gi.repository import Budgie, GObject, Wnck, Gtk, Gdk
import executor as Executor
import check_displays as CDisplay
import os
from stat import *

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
    manager = None

    def getFileReadWritePermission(self, path):
        os.chmod(path, S_IRUSR | S_IWUSR | S_IROTH)

    def saveBrightnessValue(self, val):
        file = open(self.file_path,"w")
        file.write("%s"%(str(val)))
        file.close()
        
    def retriveBrightnessValue(self):
        if(os.path.isfile(self.file_path)):
            file = open(self.file_path,"r")
            file.seek(0)
            val = file.read() 
            file.close()
            if (val == None):
                val = "0.5"
            if (val == ""):
                val = "0.5"
            return float("%s"%(val)) 
        else:
            return float("0.5") 

    def __assign_displays(self):
        #assigns display name
        self.displays = CDisplay.detect_display_devices()
        self.no_of_displays = len(self.displays)
        self.no_of_connected_dev = self.no_of_displays
        if self.no_of_displays is 1:
            self.display1 = self.displays[0]
        elif self.no_of_displays is 2:
            self.display1 = self.displays[0]
            self.display2 = self.displays[1]        

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)
        
        #about files
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.file_path = self.dir_path + "/ubrightnesscontroller"
        self.image_path = self.dir_path + "/brightness.svg"
        self.getFileReadWritePermission(self.file_path)
        
        #about displays
        self.display1 = None
        self.display2 = None
        self.no_of_connected_dev = 0
        self.__assign_displays()
        self.box = Gtk.EventBox()
        
        #about ui
        self.iconImage = Gtk.Image()
        self.iconImage.set_from_file(self.image_path)
        #self.iconImage = Gtk.Image.new_from_icon_name("display-brightness-symbolic", Gtk.IconSize.BUTTON)
        self.box.add(self.iconImage)
        self.box.show_all()
        self.add(self.box)
        self.popover = Budgie.Popover.new(self.box)
        self.popover.set_default_size(70, 300)

        # Gtk.Adjustment(initial value - won't work properly I'm also using set_value() below, min value, max value, step increment - press cursor keys to see!, page increment - click around the handle to see!, age size - not used here)
        gtkAdjustment = Gtk.Adjustment(50, 10, 100, 5, 0.1, 0) 
        
        # a vertical scale
        self.v_scale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=gtkAdjustment)
        
        # that can expand vertically if there is space in the grid (see below)
        self.v_scale.set_value_pos(Gtk.PositionType.BOTTOM)
        self.v_scale.set_draw_value (False)
        self.v_scale.set_vexpand(True)
        self.v_scale.set_hexpand(True)
        self.v_scale.set_inverted(True)
        
        # we connect the signal "value-changed" emitted by the scale with the callback function scale_moved
        self.v_scale.connect("value-changed", self.scale_moved)
        
        # a label
        self.label = Gtk.Label()
        self.label.set_text("")
       
        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_column_homogeneous(True)
        grid.attach(self.v_scale, 0, 0, 1, 1)
        grid.attach(self.label, 0, 1, 1, 1)
        
        self.popover.add(grid)
        self.popover.get_child().show_all()
        self.box.show_all()
        self.show_all()
        self.box.connect("button-press-event", self.on_press)
        
        self.brightnessValue = self.retriveBrightnessValue()
        self.setBrightness()
        self.v_scale.set_value(self.brightnessValue * 100)

    def setBrightness(self):
        # Change brightness
        cmd_value = "xrandr --output %s --brightness %s" % (self.display1, self.brightnessValue)
        Executor.execute_command(cmd_value)

    # any signal from the scales is signaled to the label the text of which is changed
    def scale_moved(self, event):
        # get brightness from scale ui element
        self.brightnessValue = self.v_scale.get_value() / 100
        self.saveBrightnessValue(self.brightnessValue)
        self.setBrightness()
        self.label.set_text("%.1f"%(self.brightnessValue * 100))

    def	on_press(self, box, e):
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
