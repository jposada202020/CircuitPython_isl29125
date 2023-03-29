# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import isl29125


i2c = board.I2C()  # uses board.SCL and board.SDA
isl = isl29125.ISL29125(i2c)

print("Current Sensing Range Value: ", bin(isl.sensing_range))
red, green, blue = isl.colors
print("Red Luminance: ", red)
print("Green Luminance: ", green)
print("Blue Luminance:", blue)
time.sleep(1)

isl.sensing_range = isl29125.LUX_375
print("Changed Sensing Range to 375 lux:", bin(isl.sensing_range))
red, green, blue = isl.colors
print("Red Luminance: ", red)
print("Green Luminance: ", green)
print("Blue Luminance:", blue)
time.sleep(1)
