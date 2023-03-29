# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import digitalio
import isl29125

# You will need to test this example with you setup as my sensor int pin does no change
# when entering or exiting the threshold window

switch_pin = digitalio.DigitalInOut(board.D9)

i2c = board.I2C()  # uses board.SCL and board.SDA
isl = isl29125.ISL29125(i2c)

print("Current High Threshold: ", isl.high_threshold)
print("Current Low Threshold: ", isl.low_threshold)
print("Setting up High Threshold to 450 Lux and Low to 10 Lux")
isl.high_threshold = 450
isl.low_threshold = 10
print("Current High Threshold: ", isl.high_threshold)
print("Current Low Threshold: ", isl.low_threshold)
isl.clear_register_flag()
while True:
    print("INT Pin Value:", switch_pin.value)

    red, green, blue = isl.colors
    print("Red Luminance: ", red)
    print("Green Luminance: ", green)
    print("Blue Luminance:", blue)

    time.sleep(0.5)
