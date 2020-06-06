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

is_down = None

mutex = None

llast_char = last_char = char = None
i = 0


class KeyTracker():
    key = ''
    last_press_time = 0
    last_release_time = 0

    def track(self, key):
        self.key = key

    def is_pressed(self):
        d = time.time() - self.last_press_time
        screen.addstr(25, 0, "DEBUG: %s" % d)
        return d < .1

    def report_key_press(self, event):
        if event == self.key:
            if not self.is_pressed():
                # on_key_press(event)
                screen.addstr(10, 20, "KEY_PRESS_EVENT")
            self.last_press_time = time.time()

    def report_key_release(self, event):
        if event == self.key:
            timer = threading.Timer(.01, self.report_key_release_callback,
                                    args=[event])
            timer.start()

    def report_key_release_callback(self, event):
        if not self.is_pressed():
            # on_key_release(event)
            screen.addstr(11, 20, "KEY_RELEASE_EVENT")
        self.last_release_time = time.time()


key_tracker = KeyTracker()
key_tracker.track(curses.KEY_RIGHT)

try:
    while True:
        # put this at the beginning since startup time will hide this lag
        time.sleep(0.01)
        i += 1

        llast_char = last_char
        last_char = char
        char = screen.getch()
        if char == ord('q'):
            break

        if llast_char == -1 and last_char == -1 and char == -1 and mutex:
            mutex = None
            if is_down:
                screen.addstr(2, 0, 'IS_DOWN %d' % i)
            else:
                screen.addstr(3, 0, 'NOT IS_DOWN %d' % i)

        if char == -1:
            screen.addstr(10, 0, 'no input! %s' % i)
            if is_down:
                screen.addstr(15, 0, "HEREHERE %s" % i)
                is_down = None

        elif char in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_UP,
                      curses.KEY_DOWN):
            key_tracker.report_key_press(char)
            if not mutex:
                screen.addstr(1, 0, 'FIRST %s %s' % (str(curses.keyname(char)), i))
            is_down = True

            # print doesn't work with curses, use addstr instead
            screen.addstr(0, 0, '%s %s' % (str(curses.keyname(char)), i))

        # elif char == curses.KEY_LEFT:
        #     screen.addstr(0, 0, 'left  %s' % i)
        # elif char == curses.KEY_UP:
        #     screen.addstr(0, 0, 'up    %s' % i)
        # elif char == curses.KEY_DOWN:
        #     screen.addstr(0, 0, 'down  %s' % i)

            screen.addstr(5, 0, "LEEROY %s" % i)
            mutex = True

finally:
    # shut down cleanly
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
