# #!/usr/bin/env python

# import curses


# def main(screen):
#     # turn off input echoing
#     curses.noecho()

#     # respond to keys immediately (don't wait for enter)
#     curses.cbreak()

#     # map arrow keys to special values
#     screen.keypad(True)

#     screen.addstr(0, 0, "Press 'q' to quit")

#     i = 0
#     while True:
#         i += 1

#         char = screen.getch()

#         if char in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT,
#                     curses.KEY_LEFT):
#             speed = 25
#             if char in (curses.KEY_UP, curses.KEY_RIGHT):
#                 speed *= -1

#             screen.addstr(1, 0, f'Driving {curses.keyname(char).decode():<20} {i}')
#         else:
#             if char == ord('q'):
#                 break


# curses.wrapper(main)


# import sys
# import functools
# import asyncio as aio

# class Prompt:
#     def __init__(self, loop=None):
#         self.loop = loop or aio.get_event_loop()
#         self.q = aio.Queue(loop=self.loop)
#         self.loop.add_reader(sys.stdin, self.got_input)

#     def got_input(self):
#         aio.ensure_future(self.q.put(sys.stdin.readline()), loop=self.loop)

#     async def __call__(self, msg, end='\n', flush=False):
#         print(msg, end=end, flush=flush)
#         return (await self.q.get()).rstrip('\n')

# prompt = Prompt()
# raw_input = functools.partial(prompt, end='', flush=True)

# async def main():
#     # wait for user to press enter
#     await prompt("press enter to continue")

#     # simulate raw_input
#     print(await raw_input('enter something:'))

# loop = aio.get_event_loop()
# loop.run_until_complete(main())
# loop.close()

# import signal
# import re
# import struct
# import select
# import os

# class MyKeyEventClass3(object):

#   def on_fd_read(self, fd):
#     recv_return = bytearray(os.read(fd, struct.calcsize(self.event_bin_format)))
#     seconds, microseconds, e_type, code, value = struct.unpack(self.event_bin_format, recv_return)
#     full_time = seconds + microseconds / 1000000
#     if e_type == 0x1:  #  0x1 == EV_KEY means key press or release.
#       d = ("RELEASE" if value == 0 else "PRESS")  #  value == 0 release, value == 1 press
#       print("Got key " + d + " from fd " + str(fd) + ": t=" + str(full_time) + "us type=" + str(e_type) + " code=" + str(code))

#   def __init__(self):
#     self.event_bin_format = 'llHHI'  #  See kernel documentation for 'struct input_event'
#     self.done = False
#     signal.signal(signal.SIGINT, self.cleanup)

#     self.poller = select.poll()
#     initial_event_mask = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR

#     with open('/proc/bus/input/devices') as f:
#       devices_file_contents = f.read()

#     files = {}
#     for handlers in re.findall(r"""H: Handlers=([^\n]+)""", devices_file_contents, re.DOTALL):
#       dev_event_file = '/dev/input/event' + re.search(r'event(\d+)', handlers).group(1)
#       if 'kbd' in handlers:
#         try:
#           files[dev_event_file] = open(dev_event_file, 'rb')
#           #  Listen for events on this socket:
#           self.poller.register(files[dev_event_file].fileno(), initial_event_mask)
#           print("Listening to " + str(dev_event_file) + " on fd " + str(files[dev_event_file].fileno()))
#         except IOError as e:
#           if e.strerror == 'Permission denied':
#             print("You don't have read permission on ({}). Are you root?".format(dev_event_file))
#             return

#     while not self.done:
#       try:
#         events = self.poller.poll(None)
#         for fd, flag in events:
#           if flag & (select.POLLIN | select.POLLPRI):
#             self.on_fd_read(fd)
#           if flag & (select.POLLHUP | select.POLLERR):
#             return #  Lost the file descriptor
#       except Exception as e:
#         return #  Probably interrupted system call

#   def cleanup(self, signum, frame):
#     self.done = True

# a = MyKeyEventClass3()

import signal
import keyboard
import time


class MyKeyEventClass1(object):
  def __init__(self):
    self.done = False
    signal.signal(signal.SIGINT, self.cleanup)
    keyboard.hook(self.my_on_key_event)
    while not self.done:
      time.sleep(1)  #  Wait for Ctrl+C

  def cleanup(self, signum, frame):
    self.done = True

  def my_on_key_event(self, e):
    print("Got key release event: " + str(e))


a = MyKeyEventClass1()
