#!/usr/bin/env python3

"""
LEGO EV3 direct commands
"""

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

if __name__ == "__main__":
    my_ev3 = ev3.EV3(protocol=const.USB)
    my_ev3.verbosity = 1

    led_sequence = [const.LED_RED, const.LED_GREEN, const.LED_ORANGE,
                    const.LED_GREEN]
    pos_color = 0

    def next_color():
        global pos_color
        ops = b''.join([
            const.opUI_Write,
            const.LED,
            led_sequence[pos_color]
        ])
        my_ev3.send_direct_cmd(ops)
        pos_color += 1
        pos_color %= len(led_sequence)

    print("*** change colors ***")
    for i in range(8):
        next_color()
        time.sleep(1)
