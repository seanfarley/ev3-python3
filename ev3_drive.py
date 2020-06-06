#!/usr/bin/env python3

import task
import time
import ev3
import ev3_vehicle

vehicle = ev3_vehicle.TwoWheelVehicle(
    0.02128,                 # radius_wheel
    0.1175,                  # tread
    protocol=ev3.constants.USB,
)

speed = 25

vehicle._drive_turn(speed, 0.25, 60, True)
time.sleep(2)
vehicle._drive_straight(speed=speed, distance=None)
time.sleep(1)
vehicle.stop()

# drive = task.concat(
#     vehicle.task_factory("turn", speed=speed, radius_turn=0.25, angle=60),
#     vehicle.task_factory("straight", speed=speed, distance=0.1),
#     # vehicle.task_factory("rotate_to", speed=speed, orientation=0),
#     vehicle.task_factory("stop", brake=True),
#     task.Sleep(0.05),
#     vehicle.task_factory("stop", brake=False)
# )
# drive.start()

# foo = vehicle.task_factory("straight", speed=speed, distance=0.05)
# foo.start().join()

