#!/usr/bin/env python

import threading
import time


i = 0


class DriveForward():
    def __init__(self):
        self.is_driving = False

    def drive(self):
        print(f"driving called {i}")
        if not self.is_driving:
            self.is_driving = True
            print(f"DRIVING! {i}")

    def stop(self):
        print(f"stoppin called {i}")
        if self.is_driving:
            self.is_driving = False
            print(f"STOPPIN! {i}")


class KeyListener():
    def __init__(self, drive):
        self.last_press_time = 0
        self.last_release_time = 0
        self.drive = drive
        self.timer = None  # threading.Timer(.01, self._callback)

    def start(self):
        # if self.timer and not self.timer.is_alive():
        self.last_press_time = time.time()
        self.drive.drive()
        # if not self.timer.is_alive():
        self.timer = threading.Timer(.01, self._callback)
        self.timer.start()

    def _callback(self):
        d = time.time() - self.last_press_time
        # print("DEBUG: %s" % d)
        print(f"DEBUG: {d}")
        if d > .1:
            # print("Haven't heard in a while, shutting down...")
            # screen.addstr(1, 0, f"Haven't heard in a while {i}")
            # self.timer.cancel()
            if self.last_press_time == 0:
                screen.addstr(12, 12, f"WAT {i}")

            self.drive.stop()
            self.last_press_time = 0
        else:
            # print("Key still pressed")
            # screen.addstr(0, 0, f"Key still pressed {i}")
            self.timer = threading.Timer(0.01, self._callback)
            self.timer.start()


d = DriveForward()
k = KeyListener(d)

k.last_press_time = time.time()

k.start()

for i in range(0, 10):
    time.sleep(.03)
    k.last_press_time = time.time()
