#!/usr/bin/env python3

# This file is part of Advanced Brightness Controller

# Copyright © 2018 Serdar ŞEN <serdarbote@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import subprocess
import os
import errno
from MyLog import MyLog


class XrandrHelper():

    TAG = "XrandrHelper"
    isAvailable = True
    dimValue = 1
    config_path = ""
    dimCacheFilePath = ""
    ubrightnesscontroller_path = ""


    def __init__(self):
        MyLog.d(self.TAG, "init")

        # about files
        try:
            self.home_dir = os.path.expanduser("~")
            self.dir_path = os.path.dirname(os.path.realpath(__file__))
            self.ubrightnesscontroller_path = self.home_dir + '/.config/budgie-advanced-brightness-controller'
            self.makeDirIfNotExist(self.ubrightnesscontroller_path)
            self.dimCacheFilePath = self.ubrightnesscontroller_path + "/dim.txt"
        except:
            MyLog.e(self.TAG, "Error:6010")

        #about displays
        self.display1 = None
        self.display2 = None
        self.noOfConnectedDev = 0
        self.assignDisplays()

	    # update
        self.update(self.retriveDimValue())

    def saveDimValue(self, val):
        if (self.dimCacheFilePath is not ""):
            try:
                file = open(self.dimCacheFilePath, "w+")
                file.write("%s" % (str(val)))
                file.close()
            except:
                MyLog.e(self.TAG, "Error:6011")

    def retriveDimValue(self):
        val = "1"
        try:
            if (self.dimCacheFilePath is not ""):
                if (os.path.isfile(self.dimCacheFilePath)):
                    file = open(self.dimCacheFilePath, "r+")
                    file.seek(0)
                    val = file.read()
                    file.close()
                    if (val == None):
                        val = "1"
                    if (val == ""):
                        val = "1"
        except:
            MyLog.e(self.TAG, "Error:6012")

        return float("%s" % (val))

    def assignDisplays(self):
        # assigns display name

        try:
            self.displays = self.detectDisplayDevices()
            self.noOfDisplays = len(self.displays)
            self.noOfConnectedDev = self.noOfDisplays
            if self.noOfDisplays is 1:
                self.display1 = self.displays[0]
            elif self.noOfDisplays is 2:
                self.display1 = self.displays[0]
                self.display2 = self.displays[1]
        except:
            MyLog.e(self.TAG, "Error:6013")
            self.setAvailable(False)

    def setDim(self):
        # Change brightness
        try:
            cmd_value = "xrandr --output %s --brightness %s" % (self.display1, self.dimValue)
            subprocess.check_output(cmd_value, shell=True)
        except:
            MyLog.e(self.TAG, "Error:6014")
            self.setAvailable(False)

    # any signal from the scales is signaled to the dimValueLabel the text of which is changed
    def update(self, dimValue):
        # get brightness from scale ui element
        if (self.isAvailable):
            self.dimValue = dimValue
            self.saveDimValue(self.dimValue)
            self.setDim()

    def makeDirIfNotExist(self, path):
        if (path is not ""):
            try:
                os.makedirs(path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise


    def setAvailable(self, b):
        self.isAvailable = b
        if (not self.isAvailable):
            MyLog.i(self.TAG, "Dim is not available")

    def detectDisplayDevices(self):
        # Detects available displays. returns connected_displays This contains the available device names compatible with xrandr

        connected_displays = []

        xrandr_output = subprocess.check_output('xrandr -q', shell=True)

        lines = xrandr_output.decode("ascii").split('\n')
        for line in lines:
            words = line.split(' ')
            for word in words:
                if word == 'connected':
                    connected_displays.append(words[0])
        return connected_displays
