from . import (
    constants,
    utils,
)

def port_motor_input(port_output: int) -> bytes:
    """
    get corresponding input motor port (from output motor port)
    """
    if port_output == constants.PORT_A:
        return utils.LCX(16)
    elif port_output == constants.PORT_B:
        return utils.LCX(17)
    elif port_output == constants.PORT_C:
        return utils.LCX(18)
    elif port_output == constants.PORT_D:
        return utils.LCX(19)
    raise ValueError("port_output needs to be one of the port numbers [1, 2, 4, 8]")
