"""
ubxsetrate.py

Simple command line utility, installed with PyPi library pyubxutils,
to configure message rates on a UBX GNSS receiver connected
to a local serial port via the UBX CFG-MSG command.

Usage:

ubxsetrate --port dev/tty.usbmodem1301 --baudrate 38400 --timeout 5 
   --msgClass 0xf1 --msgID 0x00 --rate 1 --verbosity 1

or (to turn off all NMEA messages):

ubxsetrate --port /dev/tty.usbmodem1301 --msgClass allnmea --rate 0

Created on 12 Dec 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from logging import getLogger

from pyubx2 import SET, UBX_CLASSES, UBX_MSGIDS, UBXMessage
from serial import Serial

from pyubxutils._version import __version__ as VERSION
from pyubxutils.exceptions import ParameterError
from pyubxutils.globals import (
    ALLNMEA,
    ALLNMEA_CLS,
    ALLUBX,
    ALLUBX_CLS,
    EPILOG,
    MINMMEA_ID,
    MINNMEA,
    MINUBX,
    MINUBX_ID,
    VERBOSITY_HIGH,
)
from pyubxutils.helpers import set_common_args


class UBXSetRate:
    """
    UBX Set Rate Class.

     Supports basic enable/disable message configuration for UBX GNSS devices
     connected to a local serial port
    """

    # pylint: disable=too-many-instance-attributes

    def __init__(self, **kwargs):
        """
        Constructor.

        :param str port: (kwarg) serial port name
        :param int baudrate: (kwarg) serial baud rate (9600)
        :param int timeout: (kwarg) serial timeout in seconds (3)
        :param int msgClass: (kwarg) message class from pyubx2.UBX_CLASSES OR
        :param str msgClass: (kwarg) special values "allubx", 'minubx", "allnmea" or "minnmea"
        :param int msgID: (kwarg) message ID from pyubx2.UBX_MSGIDS[1:]
        :param int rate: (kwarg) message rate per navigation solution (1)
        :raises: ParameterError
        """

        self.logger = getLogger(__name__)
        try:
            self._serialOut = None
            self._port = kwargs.get("port")
            self._baudrate = int(kwargs.get("baudrate", 9600))
            self._timeout = int(kwargs.get("timeout", 3))
            mcls = kwargs.get("msgClass")
            mid = kwargs.get("msgID", 0)

            if mcls.lower() in (ALLNMEA, ALLUBX, MINNMEA, MINUBX):
                self._msgClass = mcls
            else:
                self._msgClass = int(mcls, 16) if mcls[0:2] == "0x" else int(mcls)
                self._msgID = int(mid, 16) if mid[0:2] == "0x" else int(mid)
                # check valid message type
                mclsb = int.to_bytes(self._msgClass, 1, byteorder="big")
                midb = int.to_bytes(
                    (self._msgClass << 8) + self._msgID, 2, byteorder="big"
                )
                if mclsb not in UBX_CLASSES or midb not in UBX_MSGIDS:
                    raise (
                        ParameterError(
                            "Unknown message type: class "
                            f"{self._msgClass} (0x{self._msgClass:02x}), "
                            f"id {self._msgID} (0x{self._msgID:02x})",
                        )
                    )
            self._rate = int(kwargs.get("rate", 1))

        except (ParameterError, ValueError, TypeError) as err:
            raise ParameterError(
                f"Invalid input arguments {kwargs}\n{err}\nType ubxsetrate -h for help."
            ) from err

    def apply(self):
        """
        Creates UBX CFG-MSG command(s) and sends them to receiver.
        """

        try:
            self.logger.info(
                f"Opening serial port {self._port} @ {self._baudrate} baud ..."
            )
            self._serialOut = Serial(self._port, self._baudrate, timeout=self._timeout)

            if self._msgClass == ALLNMEA:  # all available NMEA messages
                for msgID in UBX_MSGIDS:
                    if msgID[:1] in ALLNMEA_CLS:
                        self._sendmsg(
                            int.from_bytes(msgID[:1], "little"),
                            int.from_bytes(msgID[1:], "little"),
                        )
            elif self._msgClass == MINNMEA:  # minimum NMEA messages
                for msgID in MINMMEA_ID:
                    self._sendmsg(0xF0, int.from_bytes(msgID[1:], "little"))
            elif self._msgClass == ALLUBX:  # all available UBX messages
                for msgID in UBX_MSGIDS:
                    if msgID[:1] in ALLUBX_CLS:
                        self._sendmsg(
                            int.from_bytes(msgID[:1], "little"),
                            int.from_bytes(msgID[1:], "little"),
                        )
            elif self._msgClass == MINUBX:  # minimum UBX messages
                for msgID in MINUBX_ID:
                    self._sendmsg(0x01, int.from_bytes(msgID[1:], "little"))
            else:  # individual defined message
                self._sendmsg(self._msgClass, self._msgID)

        except Exception as err:
            raise err from err
        finally:
            if self._serialOut is not None:
                self.logger.info("Configuration message(s) sent.")
                self._serialOut.close()

    def _sendmsg(self, msgClass: int, msgID: int):
        """
        Send individual CFG-MSG command to receiver

        :param int msgClass: message class
        :param int msgID: message ID
        """

        msg = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=msgClass,
            msgID=msgID,
            rateDDC=self._rate,
            rateUART1=self._rate,
            rateUART2=self._rate,
            rateUSB=self._rate,
            rateSPI=self._rate,
        )

        self.logger.info(f"Sending configuration message {msg}...")
        self._serialOut.write(msg.serialize())


def main():
    """
    CLI Entry point.

    :param: as per UBXSetRate constructor.
    :raises: ParameterError if parameters are invalid
    """
    # pylint: disable=raise-missing-from

    ap = ArgumentParser(epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
    ap.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    ap.add_argument("-P", "--port", required=True, help="Serial port")
    ap.add_argument(
        "--baudrate",
        required=False,
        help="Serial baud rate",
        type=int,
        choices=[4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800],
        default=9600,
    )
    ap.add_argument(
        "--timeout",
        required=False,
        help="Serial timeout in seconds",
        type=float,
        default=3.0,
    )
    ap.add_argument(
        "--msgClass",
        required=True,
        help=(
            "Message class from pyubx2.UBX_CLASSES or "
            "special values 'allubx', 'minubx', 'allnmea' or 'minnmea'"
        ),
    )
    ap.add_argument(
        "--msgID", required=False, help="Message ID from pyubx2.UBX_MSGIDS[1:]"
    )
    ap.add_argument(
        "--rate",
        required=False,
        help="Message rate per navigation solution",
        type=int,
        default=1,
    )

    kwargs = set_common_args("ubxsetrate", ap, logdefault=VERBOSITY_HIGH)

    try:
        usr = UBXSetRate(**kwargs)
        usr.apply()

    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
