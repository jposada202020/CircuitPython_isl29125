# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`isl29125`
================================================================================

CircuitPython driver for the ISL29125 Sensor


* Author(s): Jose D. Montoya

Implementation Notes
--------------------


* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""

from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing_extensions import NoReturn
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_isl29125.git"

_I2C_ADDR = const(0x44)
_REG_WHOAMI = const(0x00)
_CONFIG1 = const(0x01)

# Operation Modes
POWERDOWN = const(0b000)
GREEN_ONLY = const(0b001)
RED_ONLY = const(0b010)
BLUE_ONLY = const(0b11)
STANDBY = const(0b100)  # No ADC Conversion
RED_GREEN_BLUE = const(0b101)
GREEN_RED = const(0b110)
GREEN_BLUE = const(0b111)


class ISL29125:
    """Driver for the ISL29125 Light Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the ISL29125 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x44`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`ISL29125` class.
    First you will need to import the libraries to use the sensor

        .. code-block:: python

            import board
            import circuitpython_isl29125.isl29125 as isl29125

    Once this is done you can define your `board.I2C` object and define your sensor object

        .. code-block:: python

            i2c = board.I2C()  # uses board.SCL and board.SDA
            isl = isl29125.ISL29125(i2c)

    Now you have access to the :attr:`colors` attribute

        .. code-block:: python

            red, green, blue = isl.colors


    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _conf_reg = UnaryStruct(_CONFIG1, "B")

    _g_LSB = ROUnaryStruct(0x09, "B")
    _g_MSB = ROUnaryStruct(0x0A, "B")
    _r_LSB = ROUnaryStruct(0x0B, "B")
    _r_MSB = ROUnaryStruct(0x0C, "B")
    _b_LSB = ROUnaryStruct(0x0D, "B")
    _b_MSB = ROUnaryStruct(0x0E, "B")

    _operation_mode = RWBits(3, _CONFIG1, 0)

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0x7D:
            raise RuntimeError("Failed to find ISL29125")

        self._conf_reg = 0x0D

    @property
    def green(self):
        """Green property"""

        return self._g_MSB * 256 + self._g_LSB

    @property
    def red(self):
        """red property"""

        return self._r_MSB * 256 + self._r_LSB

    @property
    def blue(self):
        """blue property"""

        return self._b_MSB * 256 + self._b_LSB

    @property
    def colors(self):
        """colors property"""

        return self.red, self.green, self.blue

    @property
    def operation_mode(self) -> int:
        """The device has various RGB operating modes. The device powers up on
        a disable mode. All operating modes are in continuous ADC
        conversion. The following bits are used to enable the operating mode


        +----------------------------------------+-------------------------+
        | Mode                                   | Value                   |
        +========================================+=========================+
        | :py:const:`isl29125.POWERDOWN`         | :py:const:`0b000`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.GREEN_ONLY`        | :py:const:`0b001`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.RED_ONLY`          | :py:const:`0b010`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.BLUE_ONLY`         | :py:const:`0b011`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.STANDBY`           | :py:const:`0b100`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.RED_GREEN_BLUE`    | :py:const:`0b101`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.GREEN_RED`         | :py:const:`0b110`       |
        +----------------------------------------+-------------------------+
        | :py:const:`isl29125.GREEN_BLUE`        | :py:const:`0b111`       |
        +----------------------------------------+-------------------------+


        Example
        ---------------------

        .. code-block:: python

            i2c = board.I2C()
            isl = isl29125.ISL29125(i2c)


            isl.operation_mode = isl29125.BLUE_ONLY


        """

        return self._operation_mode

    @operation_mode.setter
    def operation_mode(self, value: int) -> NoReturn:

        self._operation_mode = value
