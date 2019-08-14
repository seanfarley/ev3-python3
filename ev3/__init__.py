import socket
import struct
import re
import threading
import time
import datetime
import hid

from . import (
    constants as const,
    error,
)

from .constants import *  # noqa


class EV3:
    """Object to communicate with a LEGO EV3 using direct commands"""

    _msg_cnt = 41
    _lock = threading.Lock()
    _foreign = {}

    def __init__(self, protocol: str = None, host: str = None, ev3_obj=None):
        """Establish a connection to a LEGO EV3 device

        Keyword Arguments (either protocol and host or ev3_obj):
        protocol: None, 'Bluetooth', 'Usb' or 'Wifi'
        host: None or mac-address of the LEGO EV3 (f.i. '00:16:53:42:2B:99')
        ev3_obj: None or an existing EV3 object (its connections will be used)
        """
        assert ev3_obj or protocol, \
            'Either protocol or ev3_obj needs to be given'
        if ev3_obj:
            assert isinstance(ev3_obj, EV3), \
                'ev3_obj needs to be instance of EV3'
            self._protocol = ev3_obj._protocol
            self._device = ev3_obj._device
            self._socket = ev3_obj._socket
        else:
            assert protocol in [const.BLUETOOTH, const.WIFI, const.USB], \
                'Protocol ' + protocol + 'is not valid'
            self._protocol = protocol
            self._device = None
            self._socket = None
            if protocol == const.BLUETOOTH:
                assert host, 'protocol ' + protocol + ' needs argument host'
                self._connect_bluetooth(host)
            elif protocol == const.WIFI:
                self._connect_wifi(host)
            else:
                self._connect_usb(host)
        self._verbosity = 0
        self._sync_mode = const.STD

    def __del__(self):
        """
        closes the connection to the LEGO EV3
        """
        if isinstance(self._socket, socket.socket):
            self._socket.close()

    @property
    def sync_mode(self) -> str:
        """
        sync mode (standard, asynchronous, synchronous)

        STD:   Use DIRECT_COMMAND_REPLY if global_mem > 0,
               wait for reply if there is one.
        ASYNC: Use DIRECT_COMMAND_REPLY if global_mem > 0,
               never wait for reply (it's the task of the calling program).
        SYNC:  Always use DIRECT_COMMAND_REPLY and wait for reply.

        The general idea is:
        ASYNC: Interruption or EV3 device queues direct commands,
               control directly comes back.
        SYNC:  EV3 device is blocked until direct command is finished,
               control comes back, when direct command is finished.
        STD:   NO_REPLY like ASYNC with interruption or EV3 queuing,
               REPLY like SYNC, synchronicity of program and EV3 device.
        """
        return self._sync_mode

    @sync_mode.setter
    def sync_mode(self, value: str):
        assert isinstance(value, str), \
            "sync_mode needs to be of type str"
        assert value in [const.STD, const.SYNC, const.ASYNC], \
            "value of sync_mode: " + value + " is invalid"
        self._sync_mode = value

    @property
    def verbosity(self) -> int:
        """
        level of verbosity (prints on stdout).
        """
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value: int):
        assert isinstance(value, int), \
            "verbosity needs to be of type int"
        assert value >= 0 and value <= 2, \
            "allowed verbosity values are: 0, 1 or 2"
        self._verbosity = value

    def _connect_bluetooth(self, host: str) -> int:
        """
        Create a socket, that holds a bluetooth-connection to an EV3
        """
        # self._socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        # self._socket.bind((host, 0))
        raise NotImplementedError("Bluetooth isn't yet implemented")

    def _connect_wifi(self, host: str) -> int:
        """
        Create a socket, that holds a wifi-connection to an EV3
        """

        # listen on port 3015 for a UDP broadcast from the EV3
        UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPSock.bind(('', 3015))
        data, addr = UDPSock.recvfrom(67)

        # pick serial number, port, name and protocol
        # from the broadcast message
        matcher = re.search(r'Serial-Number: (\w*)\s\n'
                            + r'Port: (\d{4,4})\s\n'
                            + r'Name: (\w+)\s\n'
                            + r'Protocol: (\w+)\s\n',
                            data.decode('utf-8'))
        serial_number = matcher.group(1)
        port = matcher.group(2)
        name = matcher.group(3)
        protocol = matcher.group(4)

        # test if correct mac-addr
        if host and serial_number.upper() != host.replace(':', '').upper():
            self._socket = None
            raise ValueError('found ev3 but not ' + host)

        # Send an UDP message back to the EV3
        # to make it accept a TCP/IP connection
        UDPSock.sendto(' '.encode('utf-8'), (addr[0], int(port)))
        UDPSock.close()

        # Establish a TCP/IP connection with EV3s address and port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((addr[0], int(port)))

        # Send an unlock message to the EV3 over TCP/IP
        msg = 'GET /target?sn=' + serial_number + 'VMTP1.0\n' + \
              'Protocol: ' + protocol
        self._socket.send(msg.encode('utf-8'))
        reply = self._socket.recv(16).decode('utf-8')
        if not reply.startswith('Accept:EV340'):
            raise RuntimeError('No wifi connection to ' + name
                               + ' established')

    def _connect_usb(self, host: str) -> int:
        """Create a device, that holds an usb-connection to an EV3"""
        ev3_devices = [h for h in hid.enumerate()
                       if h['vendor_id'] == const.ID_VENDOR_LEGO]

        found_host = None
        for dev in ev3_devices:
            if found_host:
                raise ValueError('found multiple ev3 but no argument'
                                 'host was set')
            if host:
                mac_addr = dev['serial_number']
                if mac_addr.upper() == host.replace(':', '').upper():
                    found_host = dev
                    break
            else:
                found_host = dev
        if not found_host:
            raise RuntimeError("Lego EV3 not found")

        self._device = hid.device()
        self._device.open(const.ID_VENDOR_LEGO, const.ID_PRODUCT_EV3,
                          found_host['serial_number'])

        # initial read
        self._device.set_nonblocking(1)
        self._device.read(1024)

    def send_direct_cmd(self, ops: bytes, local_mem: int = 0,
                        global_mem: int = 0) -> bytes:
        """Send a direct command to the LEGO EV3

        Arguments:
        ops: holds netto data only (operations), the following fields are
             added:
          length: 2 bytes, little endian
          counter: 2 bytes, little endian
          type: 1 byte, DIRECT_COMMAND_REPLY or DIRECT_COMMAND_NO_REPLY
          header: 2 bytes, holds sizes of local and global memory

        Keyword Arguments:
        local_mem: size of the local memory
        global_mem: size of the global memory

        Returns:
          sync_mode is STD: reply (if global_mem > 0) or message counter
          sync_mode is ASYNC: message counter
          sync_mode is SYNC: reply of the LEGO EV3
        """
        if global_mem > 0 or self._sync_mode == const.SYNC:
            cmd_type = const.DIRECT_COMMAND_REPLY
        else:
            cmd_type = const.DIRECT_COMMAND_NO_REPLY
        self._lock.acquire()
        if self._msg_cnt < 65535:
            self._msg_cnt += 1
        else:
            self._msg_cnt = 1
        msg_cnt = self._msg_cnt
        self._lock.release()
        cmd = b''.join([
            struct.pack('<hh', len(ops) + 5, msg_cnt),
            cmd_type,
            struct.pack('<h', local_mem * 1024 + global_mem),
            ops
        ])
        if self._verbosity >= 1:
            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now
                  + ' Sent 0x|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[5:7]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[7:]) + '|')
        if self._protocol in [const.BLUETOOTH, const.WIFI]:
            self._socket.send(cmd)
        elif self._protocol is const.USB:
            self._device.write(list(cmd) + [0] * 100)
        else:
            raise RuntimeError('No EV3 connected')
        counter = cmd[2:4]
        if (cmd[4:5] == const.DIRECT_COMMAND_NO_REPLY
            or self._sync_mode == const.ASYNC):
            return counter
        else:
            return self.wait_for_reply(counter)

    def wait_for_reply(self, counter: bytes) -> bytes:
        """Ask the LEGO EV3 for a reply and wait until it is received

        Arguments:
        counter: is the message counter of the corresponding send_direct_cmd

        Returns:
        reply to the direct command
        """
        self._lock.acquire()
        reply = self._get_foreign_reply(counter)
        if reply:
            self._lock.release()
            if reply[4:5] != const.DIRECT_REPLY:
                raise error.DirCmdError(
                    "direct command {:02X}:{:02X} replied error".format(
                        reply[2],
                        reply[3]
                    )
                )
            return reply
        loop_counter = 0
        while True:
            if self._protocol in [const.BLUETOOTH, const.WIFI]:
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(1024))
            try:
                len_data = struct.unpack('<H', reply[:2])[0] + 2
            except struct.error:
                time.sleep(0.01)
                loop_counter += 1
                if loop_counter > 100:
                    raise Exception("More than %d loops with no response" % loop_counter)
                continue


            reply_counter = reply[2:4]
            if self._verbosity >= 1:
                now = datetime.datetime.now().strftime('%H:%M:%S.%f')
                print(now
                      + ' Recv 0x|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[0:2])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[2:4])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[4:5])
                      + '|', end='')
                if len_data > 5:
                    dat = ':'.join('{:02X}'.format(byte)
                                   for byte in reply[5:len_data])
                    print(dat + '|')
                else:
                    print()
            if counter != reply_counter:
                self._put_foreign_reply(reply_counter, reply[:len_data])
            else:
                self._lock.release()
                if reply[4:5] != const.DIRECT_REPLY:
                    raise error.DirCmdError(
                        "direct command {:02X}:{:02X} replied error".format(
                            reply[2],
                            reply[3]
                        )
                    )
                return reply[:len_data]

    def send_system_cmd(self, cmd: bytes, reply: bool = True) -> bytes:
        """Send a system command to the LEGO EV3

        Arguments:
        cmd: holds netto data only (cmd and arguments), the following fields
             are added:
          length: 2 bytes, little endian
          counter: 2 bytes, little endian
          type: 1 byte, SYSTEM_COMMAND_REPLY or SYSTEM_COMMAND_NO_REPLY

        Keyword Arguments:
        reply: flag if with reply

        Returns:
          reply (in case of SYSTEM_COMMAND_NO_REPLY: counter)
        """
        if reply:
            cmd_type = const.SYSTEM_COMMAND_REPLY
        else:
            cmd_type = const.SYSTEM_COMMAND_NO_REPLY
        self._lock.acquire()
        if self._msg_cnt < 65535:
            self._msg_cnt += 1
        else:
            self._msg_cnt = 1
        msg_cnt = self._msg_cnt
        self._lock.release()
        cmd = b''.join([
            struct.pack('<hh', len(cmd) + 3, msg_cnt),
            cmd_type,
            cmd
        ])
        if self._verbosity >= 1:
            now = datetime.datetime.now().strftime('%H:%M:%S.%f')
            print(now
                  + ' Sent 0x|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[0:2]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[2:4]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[4:5]) + '|'
                  + ':'.join('{:02X}'.format(byte) for byte in cmd[5:]) + '|')
        if self._protocol in [const.BLUETOOTH, const.WIFI]:
            self._socket.send(cmd)
        elif self._protocol is const.USB:
            self._device.write(list(cmd) + [0] * 100)
        else:
            raise RuntimeError('No EV3 connected')
        counter = cmd[2:4]
        if not reply:
            return counter
        else:
            reply = self._wait_for_system_reply(counter)
            return reply

    def _wait_for_system_reply(self, counter: bytes) -> bytes:
        """Ask the LEGO EV3 for a system command reply and wait until received

        Arguments:
        counter: is the message counter of the corresponding send_system_cmd

        Returns:
        reply to the system command
        """
        self._lock.acquire()
        reply = self._get_foreign_reply(counter)
        if reply:
            self._lock.release()
            if reply[4:5] != const.SYSTEM_REPLY:
                raise error.SysCmdError("error: {:02X}".format(reply[6]))
            return reply
        if self._protocol == const.BLUETOOTH:
            time.sleep(0.1)
        while True:
            if self._protocol in [const.BLUETOOTH, const.WIFI]:
                reply = self._socket.recv(1024)
            else:
                reply = bytes(self._device.read(1024))
            len_data = struct.unpack('<H', reply[:2])[0] + 2
            reply_counter = reply[2:4]
            if self._verbosity >= 1:
                now = datetime.datetime.now().strftime('%H:%M:%S.%f')
                print(now
                      + ' Recv 0x|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[0:2])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[2:4])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[4:5])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[5:6])
                      + '|'
                      + ':'.join('{:02X}'.format(byte) for byte in reply[6:7])
                      + '|', end='')
                if len_data > 7:
                    dat = ':'.join('{:02X}'.format(byte)
                                   for byte in reply[7:len_data])
                    print(dat + '|')
                else:
                    print()
            if counter != reply_counter:
                self._put_foreign_reply(reply_counter, reply[:len_data])
            else:
                self._lock.release()
                if reply[4:5] != const.SYSTEM_REPLY:
                    raise error.SysCmdError("system command replied "
                                            "error: {:02X}".format(reply[6]))
                return reply[:len_data]

    def _put_foreign_reply(self, counter: bytes, reply: bytes) -> None:
        """
        put a foreign reply to the stack
        """
        if counter in self._foreign:
            raise ValueError('reply with counter ' + str(counter)
                             + ' already exists')
        else:
            self._foreign[counter] = reply

    def _get_foreign_reply(self, counter: bytes) -> bytes:
        """
        get a reply from the stack (returns None if there is no)
        and delete this reply from the stack
        """
        if counter in self._foreign:
            reply = self._foreign[counter]
            del self._foreign[counter]
            return reply

        return None
