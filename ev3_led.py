#!/usr/bin/env python3

"""Python script to cycle through LEGO EV3 LED colors """

# Copyright (C) 2016 Christoph Gaukel <christoph.gaukel@gmx.de>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import time

import ev3
import ev3.constants as const


class led_changer():
    """Iterator to cyle through the LED colors on an EV3"""

    led_sequence = [const.LED_RED, const.LED_GREEN, const.LED_ORANGE,
                    const.LED_GREEN]

    def __init__(self, end: int = 4):
        self.pos_color = None
        self.end = end

    def __iter__(self):
        self.pos_color = 0
        return self

    def __next__(self):
        ops = b''.join([
            const.opUI_Write,
            const.LED,
            self.led_sequence[self.pos_color % len(self.led_sequence)]
        ])
        self.pos_color += 1
        if self.pos_color > self.end:
            raise StopIteration
        return ops



def main():
    my_ev3 = ev3.EV3(protocol=const.USB)
    my_ev3.verbosity = 1

    print("*** change colors ***")
    for cmd in led_changer(8):
        my_ev3.send_direct_cmd(cmd)
        time.sleep(1)


if __name__ == "__main__":
    main()
