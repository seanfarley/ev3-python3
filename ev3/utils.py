import struct


class PID():
    """
    object to implement a PID controller
    """
    # pylint: disable=too-many-arguments
    def __init__(
            self,
            setpoint: float,
            gain_prop: float,
            gain_der: float=None,
            gain_int: float=None,
            half_life: float=None
    ):
        """
        Parametrizes a new PID controller

        Arguments:
        setpoint: ideal value of the process variable
        gain_prop: proportional gain,
                   high values result in fast adaption,
                   but too high values produce oscillations or instabilities

        Keyword Arguments:
        gain_der: gain of the derivative part [s], decreases overshooting and settling time
        gain_int: gain of the integrative part [1/s], eliminates steady-state error,
                  slower and smoother response
        half_life: used for discrete or noisy systems, smooths actual values [s]
        """
        self._setpoint = setpoint
        self._gain_prop = gain_prop
        self._gain_int = gain_int
        self._gain_der = gain_der
        self._half_life = half_life
        self._error = None
        self._time = None
        self._int = None
        self._value = None
    # pylint: enable=too-many-arguments

    def control_signal(self, actual_value: float) -> float:
        """
        calculates the control signal from the actual value

        Arguments:
        actual_value: actual measured process variable (will be compared to setpoint)

        Returns:
        control signal, which will be sent to the process
        """
        if self._value is None:
            self._value = actual_value
            self._time = time.time()
            self._int = 0
            self._error = self._setpoint - actual_value
            return self._gain_prop * self._error
        else:
            time_act = time.time()
            delta_time = time_act - self._time
            self._time = time_act
            if self._half_life is None:
                self._value = actual_value
            else:
                fact1 = math.log(2) / self._half_life
                fact2 = math.exp(-fact1 * delta_time)
                self._value = fact2 * self._value + actual_value * (1 - fact2)
            error = self._setpoint - self._value
            if self._gain_int is None:
                signal_int = 0
            else:
                self._int += error * delta_time
                signal_int = self._gain_int * self._int
            if self._gain_der is None:
                signal_der = 0
            else:
                signal_der = self._gain_der * (error - self._error) / delta_time
            self._error = error
            return self._gain_prop * error + signal_int + signal_der


def LCX(value: int) -> bytes:
    """create a LC0, LC1, LC2, LC4, dependent from the value"""
    if   value >=    -32 and value <      0:
        return struct.pack('b', 0x3F & (value + 64))
    elif value >=      0 and value <     32:
        return struct.pack('b', value)
    elif value >=   -127 and value <=   127:
        return b'\x81' + struct.pack('<b', value)
    elif value >= -32767 and value <= 32767:
        return b'\x82' + struct.pack('<h', value)
    else:
        return b'\x83' + struct.pack('<i', value)


def LCS(value: str) -> bytes:
    """
    pack a string into a LCS
    """
    return b'\x84' + str.encode(value) + b'\x00'


def LVX(value: int) -> bytes:
    """
    create a LV0, LV1, LV2, LV4, dependent from the value
    """
    if value   <     0:
        raise RuntimeError('No negative values allowed')
    elif value <    32:
        return struct.pack('b', 0x40 | value)
    elif value <   256:
        return b'\xc1' + struct.pack('<b', value)
    elif value < 65536:
        return b'\xc2' + struct.pack('<h', value)
    else:
        return b'\xc3' + struct.pack('<i', value)


def GVX(value: int) -> bytes:
    """create a GV0, GV1, GV2, GV4, dependent from the value"""
    if value   <     0:
        raise RuntimeError('No negative values allowed')
    elif value <    32:
        return struct.pack('<b', 0x60 | value)
    elif value <   256:
        return b'\xe1' + struct.pack('<b', value)
    elif value < 65536:
        return b'\xe2' + struct.pack('<h', value)
    else:
        return b'\xe3' + struct.pack('<i', value)
