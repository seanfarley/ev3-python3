#!/usr/bin/env python3

import curses

# import ev3
# import ev3_vehicle


def main(screen):

    # vehicle = ev3_vehicle.TwoWheelVehicle(
    #     0.02128,                 # radius_wheel
    #     0.1175,                  # tread
    #     protocol=ev3.constants.USB,
    # )

    # turn off input echoing
    curses.noecho()

    # respond to keys immediately (don't wait for enter)
    curses.cbreak()

    # map arrow keys to special values
    screen.keypad(True)

    screen.addstr(0, 0, "Press 'q' to quit")

    i = 0
    while True:
        i += 1

        char = screen.getch()

        if char in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_RIGHT,
                    curses.KEY_LEFT):
            speed = 25
            if char in (curses.KEY_UP, curses.KEY_RIGHT):
                speed *= -1

            screen.addstr(1, 0, f'Driving {curses.keyname(char).decode():<20} {i}')
            # if char in (curses.KEY_UP, curses.KEY_DOWN):
            #     vehicle._drive_straight(speed, 0.1)
            # else:
            #     vehicle._drive_turn(speed, 0.25, 60, speed < 0)
        else:
            # vehicle.stop()
            if char == ord('q'):
                break


curses.wrapper(main)
