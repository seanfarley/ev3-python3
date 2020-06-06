import curses
import threading
import time


# get the curses screen window
screen = curses.initscr()

# turn off input echoing
curses.noecho()

# respond to keys immediately (don't wait for enter)
curses.cbreak()

# map arrow keys to special values
screen.keypad(True)

# non-blocking getch
screen.nodelay(True)

i = 0


class DriveForward():
    def __init__(self):
        self.is_driving = False

    def drive(self):
        screen.addstr(10, 0, f"driving called {i}")
        if not self.is_driving:
            self.is_driving = True
            screen.addstr(0, 0, f"DRIVING! {i}")

    def stop(self):
        screen.addstr(11, 0, f"stoppin called {i}")
        if self.is_driving:
            self.is_driving = False
            screen.addstr(0, 0, f"STOPPIN! {i}")


class KeyListener():
    def __init__(self, drive):
        self.last_press_time = 0
        self.last_release_time = 0
        self.drive = drive
        self.timer = None  # threading.Timer(.01, self._callback)

    def start(self):
        # if self.timer and not self.timer.is_alive():
        # self.last_press_time = time.time()
        # self.drive.drive()
        # if not self.timer.is_alive():
        self.timer = threading.Timer(.1, self._callback)
        self.timer.start()

    def _callback(self):
        d = time.time() - self.last_press_time
        # print("DEBUG: %s" % d)
        screen.addstr(0, 40, f"DEBUG: {d}")
        if d > .2 and self.last_press_time != 0:
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

try:
    char = screen.getch()
    while True:
        # put this at the beginning since startup time will hide this lag
        time.sleep(0.01)
        i += 1

        if char in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP,
                    curses.KEY_DOWN):
            k.last_press_time = time.time()
            k.start()
            # if not k.timer.is_alive():
            # if k.timer is None:
            # k.start()

        char = screen.getch()
        if char == ord('q'):
            break


finally:
    # shut down cleanly
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
