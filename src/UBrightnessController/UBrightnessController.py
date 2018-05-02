#!/usr/bin/env python3

# This file is part of budgie-browser-profile-launcher

# Copyright © 2015-2017 Ikey Doherty <ikey@solus-project.com>
# Copyright © 2018 Serdar ŞEN <serdarbote@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import gi.repository
gi.require_version('Budgie', '1.0')
from gi.repository import Budgie, GObject, Gtk, Gdk
from BackLightHelper import BackLightHelper
from XrandrHelper import XrandrHelper
from MyLog import MyLog


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

    def budgie_popover_key_press(self, widget, key, udata):
        MyLog.d(self.TAG, "budgie_popover_key_press")

class UBrightnessControllerApplet(Budgie.Applet):
    #Budgie.Applet is in fact a Gtk.Bin

    TAG = "UBrightnessControllerApplet"
    manager = None

    def __init__(self, uuid):

        Budgie.Applet.__init__(self)

        self.backLightHelper = BackLightHelper()
        self.xrandrHelper = XrandrHelper()

        self.indicatorBox = Gtk.EventBox()
        self.iconIndicator = Gtk.Image.new_from_icon_name("u-brightness-controller-1-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        self.indicatorBox.add(self.iconIndicator)
        self.indicatorBox.show_all()
        self.add(self.indicatorBox)
        self.popover = Budgie.Popover.new(self.indicatorBox)
        self.indicatorBox.connect("button-press-event", self.indicatorBoxOnClick)

        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_column_homogeneous(True)
        grid.set_margin_top(5)
        grid.set_margin_bottom(5)
        grid.set_margin_left(5)
        grid.set_margin_right(5)


        if(self.backLightHelper.isAvailable and self.xrandrHelper.isAvailable):
            self.popover.set_default_size(140, 300)
        elif(self.backLightHelper.isAvailable or self.xrandrHelper.isAvailable):
            self.popover.set_default_size(70, 300)


        if(self.xrandrHelper.isAvailable):
            # Gtk.Adjustment(initial value - won't work properly I'm also using set_value() below, min value, max value, step increment - press cursor keys to see!, page increment - click around the handle to see!, age size - not used here)
            gtkAdjustmentForDimScale = Gtk.Adjustment(50, 10, 100, 5, 0.1, 0) 
            # a vertical scale
            self.dimScale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=gtkAdjustmentForDimScale)
            # that can expand vertically if there is space in the grid (see below)
            self.dimScale.set_value_pos(Gtk.PositionType.BOTTOM)
            self.dimScale.set_draw_value (False)
            self.dimScale.set_vexpand(True)
            self.dimScale.set_hexpand(True)
            self.dimScale.set_inverted(True)
            # we connect the signal "value-changed" emitted by the scale with the callback function scale_moved
            self.dimScale.connect("value-changed", self.dimScaleMoved)
            # value labels
            self.dimValueLabel = Gtk.Label()
            self.dimValueLabel.set_text("")
            self.dimTitleLabel = Gtk.Label()
            self.dimTitleLabel.set_text("Dim")
            self.dimScale.set_value(self.xrandrHelper.retriveDimValue() * 100)


        if(self.backLightHelper.isAvailable):
            gtkAdjustmentForBrightnessScale = Gtk.Adjustment(2, 0, self.backLightHelper.getMaxBrightness(), 5, 1, 0)
            self.brightnessScale = Gtk.Scale(orientation=Gtk.Orientation.VERTICAL, adjustment=gtkAdjustmentForBrightnessScale)
            self.brightnessScale.set_value_pos(Gtk.PositionType.BOTTOM)
            self.brightnessScale.set_draw_value (False)
            self.brightnessScale.set_vexpand(True)
            self.brightnessScale.set_hexpand(True)
            self.brightnessScale.set_inverted(True)
            self.brightnessScale.connect("value-changed", self.brightnessScaleMoved)
            self.brightnessValueLabel = Gtk.Label()
            self.brightnessValueLabel.set_text("")
            self.brightnessTitleLabel = Gtk.Label()
            self.brightnessTitleLabel.set_text("Light")
            self.brightnessScale.set_value(self.backLightHelper.getCurrentBrightness())

        if(self.backLightHelper.isAvailable and self.xrandrHelper.isAvailable):
            #Brightness
            grid.attach(self.brightnessTitleLabel, 0, 0, 1, 1)
            grid.attach(self.brightnessScale, 0, 1, 1, 1)
            grid.attach(self.brightnessValueLabel, 0, 2, 1, 1)

            #Dim
            grid.attach(self.dimTitleLabel, 1, 0, 1, 1)
            grid.attach(self.dimScale, 1, 1, 1, 1)
            grid.attach(self.dimValueLabel, 1, 2, 1, 1)

        elif(self.xrandrHelper.isAvailable and not self.backLightHelper.isAvailable):
            #Dim
            grid.attach(self.dimTitleLabel, 0, 0, 1, 1)
            grid.attach(self.dimScale, 0, 1, 1, 1)
            grid.attach(self.dimValueLabel, 0, 2, 1, 1)

        elif(self.backLightHelper.isAvailable and not self.xrandrHelper.isAvailable):
            #Brightness
            grid.attach(self.brightnessTitleLabel, 0, 0, 1, 1)
            grid.attach(self.brightnessScale, 0, 1, 1, 1)
            grid.attach(self.brightnessValueLabel, 0, 2, 1, 1)

        self.popover.add(grid)
        self.popover.get_child().show_all()
        self.indicatorBox.show_all()
        self.show_all()

    def indicatorBoxOnClick(self, box, e):
        self.updadeBrightness()
        if e.button != 1:
            return Gdk.EVENT_PROPAGATE
        if self.popover.get_visible():
            self.popover.hide()
        else:
            self.manager.show_popover(self.indicatorBox)
        return Gdk.EVENT_STOP

    # any signal from the scales is signaled to the dimValueLabel the text of which is changed
    def brightnessScaleMoved(self, event):
        self.backLightHelper.update(self.brightnessScale.get_value())
        self.brightnessValueLabel.set_text("%.0f" % self.brightnessScale.get_value())
        MyLog.d(self.TAG, "brightnessScaleMoved %.0f" % self.brightnessScale.get_value())

    def dimScaleMoved(self, event):
        # get brightness from scale ui element
        self.xrandrHelper.update(self.dimScale.get_value() / 100)
        self.dimValueLabel.set_text("%.1f" % self.dimScale.get_value())
        MyLog.d(self.TAG, "dimScaleMoved %.1f" % self.dimScale.get_value())


    def do_update_popovers(self, manager):
        self.manager = manager
        self.manager.register_popover(self.indicatorBox, self.popover)


    def updadeBrightness(self):
        brightness = self.backLightHelper.getCurrentBrightnessFromHelper()
        self.backLightHelper.update(brightness)
        self.brightnessValueLabel.set_text("%.0f" % brightness)
        self.brightnessScale.set_value(brightness)
        MyLog.d(self.TAG, "updadeBrightness %.0f" % brightness)
