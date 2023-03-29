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
_CONFIG2 = const(0x02)

# Operation Modes
POWERDOWN = const(0b000)
GREEN_ONLY = const(0b001)
RED_ONLY = const(0b010)
BLUE_ONLY = const(0b11)
STANDBY = const(0b100)  # No ADC Conversion
RED_GREEN_BLUE = const(0b101)
GREEN_RED = const(0b110)
GREEN_BLUE = const(0b111)

# Sensing Range
LUX_375 = const(0b0)
LUX_10K = const(0b1)

# ADC Resolution
RES_16BITS = const(0b0)
RES_12BITS = const(0b1)


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
    _conf_reg2 = UnaryStruct(_CONFIG2, "B")

    _g_LSB = ROUnaryStruct(0x09, "B")
    _g_MSB = ROUnaryStruct(0x0A, "B")
    _r_LSB = ROUnaryStruct(0x0B, "B")
    _r_MSB = ROUnaryStruct(0x0C, "B")
    _b_LSB = ROUnaryStruct(0x0D, "B")
    _b_MSB = ROUnaryStruct(0x0E, "B")

    _operation_mode = RWBits(3, _CONFIG1, 0)
    _rgb_sensing_range = RWBits(1, _CONFIG1, 3)
    _adc_resolution = RWBits(1, _CONFIG1, 3)
    _ir_compensation = RWBits(1, _CONFIG2, 7)
    _ir_compensation_value = RWBits(6, _CONFIG2, 0)

    def __init__(self, i2c_bus: I2C, address: int = _I2C_ADDR) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0x7D:
            raise RuntimeError("Failed to find ISL29125")

        self._conf_reg = 0x0D
        # 0xBF Datasheet recommendation to max out IR compensation value.
        # It makes High range reach more than 10,000lux.
        self._conf_reg2 = 0xBF

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

    @property
    def sensing_range(self) -> int:
        """The Full Scale RGB Range has two different selectable ranges at bit 3.
         The range determines the ADC resolution (12 bits and 16 bits).
         Each range has a maximum allowable lux value. Higher range values offer
         better resolution and wider lux value


        +----------------------------------------+----------------------------------+
        | Mode                                   | Value                            |
        +========================================+==================================+
        | :py:const:`isl29125.LUX_375`           | :py:const:`0b0` 375 lux          |
        +----------------------------------------+----------------------------------+
        | :py:const:`isl29125.LUX_10K`           | :py:const:`0b1` 10000 lux        |
        +----------------------------------------+----------------------------------+


        Example
        ---------------------

        .. code-block:: python

            i2c = board.I2C()
            isl = isl29125.ISL29125(i2c)


            isl.operation_mode = isl29125.LUX_375


        """

        return self._rgb_sensing_range

    @sensing_range.setter
    def sensing_range(self, value: int) -> NoReturn:

        self._rgb_sensing_range = value

    @property
    def adc_resolution(self) -> int:
        """ADC’s resolution and the number of clock cycles per conversion is
        determined by this bit. Changing the resolution of the ADC, changes the
        number of clock cycles of the ADC which in turn changes the integration time.
        Integration time is the period the ADC samples the photodiode current signal
        for a measurement


        +----------------------------------------+----------------------------------+
        | Mode                                   | Value                            |
        +========================================+==================================+
        | :py:const:`isl29125.RES_12BITS`        | :py:const:`0b0` 16 bits          |
        +----------------------------------------+----------------------------------+
        | :py:const:`isl29125.RES_16BITS`        | :py:const:`0b1` 12 bits          |
        +----------------------------------------+----------------------------------+


        Example
        ---------------------

        .. code-block:: python

            i2c = board.I2C()
            isl = isl29125.ISL29125(i2c)


            isl.operation_mode = isl29125.RES_12BITS


        """

        return self._adc_resolution

    @adc_resolution.setter
    def adc_resolution(self, value: int) -> NoReturn:

        self._adc_resolution = value

    @property
    def ir_compensation(self) -> int:
        """The device provides a programmable active IR compensation which allows fine-tuning
         of residual infrared components from the output which allows optimizing the measurement
          variation between differing IR-content light sources.

        +----------------------------------------+----------------------------------+
        | Mode                                   | Value                            |
        +========================================+==================================+
        | :py:const:`isl29125.IR_ON`             | :py:const:`0b1`                  |
        +----------------------------------------+----------------------------------+
        | :py:const:`isl29125.IR_OFF`            | :py:const:`0b0`                  |
        +----------------------------------------+----------------------------------+


        Example
        ---------------------

        .. code-block:: python

            i2c = board.I2C()
            isl = isl29125.ISL29125(i2c)


            isl.ir_compensation = isl29125.IR_ON


        """

        return self._ir_compensation

    @ir_compensation.setter
    def ir_compensation(self, value: int) -> NoReturn:

        self._ir_compensation = value

    @property
    def ir_compensation_value(self) -> int:
        """The effective IR compensation is from 106 to 169 in the CONF2 register.
        Consult datasheet for detailed IR filtering calibration

        with the following values:

        * BIT5: 32
        * BIT4: 16
        * BIT3: 8
        * BIT2: 4
        * BIT1: 2
        * BIT0: 1


        Example
        ---------------------

        .. code-block:: python

            i2c = board.I2C()
            isl = isl29125.ISL29125(i2c)


            isl._ir_compensation_value = 48


        """

        return self._ir_compensation_value

    @ir_compensation_value.setter
    def ir_compensation_value(self, value: int) -> NoReturn:

        self._ir_compensation_value = value
