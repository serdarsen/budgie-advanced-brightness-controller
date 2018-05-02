#!/usr/bin/env python3

# This file is part of U Brightness Controller

# Copyright © 2018 Serdar ŞEN <serdarbote@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

import subprocess
from MyLog import MyLog


class BackLightHelper():

    TAG = "BackLightHelper"
    isAvailable = True
    maxBrightness = 0
    currentBrightness = 0


    def __init__(self):

        self.maxBrightness = self.getMaxBrightnessFromHelper()
        self.currentBrightness = self.getCurrentBrightnessFromHelper()

    def setAvailable(self, b):
        self.isAvailable = b
        if (not self.isAvailable):
            MyLog.i(self.TAG, "No backlight detected")

    def getMaxBrightness(self):
        return self.maxBrightness

    def getMaxBrightnessFromHelper(self):
        maxBrightness = 0
        try:
            p = subprocess.Popen(
                ['pkexec', '/usr/lib/gnome-settings-daemon/gsd-backlight-helper', '--get-max-brightness'],
                stdout=subprocess.PIPE)
            comm = p.communicate()[0]
            maxBrightness = int(comm)
        except:
            MyLog.e(self.TAG, "Error:6030")
            self.setAvailable(False)

        return maxBrightness

    def getCurrentBrightness(self):
        return self.currentBrightness

    def getCurrentBrightnessFromHelper(self):
        try:
            p = subprocess.Popen(['pkexec', '/usr/lib/gnome-settings-daemon/gsd-backlight-helper', '--get-brightness'], stdout=subprocess.PIPE)
            comm = p.communicate()[0]
            self.currentBrightness = int(comm)
        except:
            MyLog.e(self.TAG, "Error:6031")
            return self.setAvailable(False)

        return self.currentBrightness

    # any signal from the scales is signaled to the dimValueLabel the text of which is changed
    def update(self, brightness):
        if (self.isAvailable):
            self.setBrightness("%.0f" % brightness)

    def setBrightness(self, brightness):
        self.currentBrightness = brightness
        try:
            subprocess.call(['pkexec', '/usr/lib/gnome-settings-daemon/gsd-backlight-helper', '--set-brightness', "%s" % self.currentBrightness])
        except:
            MyLog.e(self.TAG, "Error:6033")
            self.setAvailable(False)

    def updateFromHelper(self):
        self.currentBrightness = self.getCurrentBrightnessFromHelper()
        self.update(self.currentBrightness)