"""
ubxbase.py

NB: ONLY FOR GENERATION 9+ UBX RTK DEVICES e.g. ZED-F9n

This command line utility configures an RTK-compatible u-blox
GNSS receiver to operate in Base Station mode.

RTCM 1006 (Antenna Reference Data) is only output if the base
station is active, so receipt of this message type is used as
a configuration success criterion.

Created on 06 Jan 2023

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2023
:license: BSD 3-Clause
"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, ArgumentTypeError
from datetime import datetime, timedelta
from logging import getLogger
from queue import Queue
from threading import Event, Thread
from time import sleep

from pyubx2 import (
    ERR_IGNORE,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    UBX_PROTOCOL,
    UBXMessage,
    UBXMessageError,
    UBXParseError,
    UBXReader,
)
from serial import Serial

from pyubxutils._version import __version__ as VERSION
from pyubxutils.exceptions import ParameterError
from pyubxutils.globals import EPILOG, VERBOSITY_HIGH
from pyubxutils.helpers import h2sphp, ll2sphp, progbar, set_common_args

ACK = "ACK-ACK"
NAK = "ACK-NAK"
DEFAULT_ACCURACY = 100
DEFAULT_DURATION = 60
DEFAULT_POS = (0.0, 0.0, 0.0)
POS_ECEF = 0
POS_LLH = 1
TMODE_DISABLED = 0
TMODE_SVIN = 1
TMODE_FIXED = 2
WAITTIME = 5  # wait time for acknowledgements
WRITETIME = 0.02  # wait time between writes


class UBXBase:
    """UBX Base Station Configuration Class."""

    def __init__(self, stream: object, **kwargs):
        """
        Constructor.

        :param object file: input file
        :param object stream: output serial stream
        """

        self.logger = getLogger(__name__)
        self._stream = stream

        self._port = kwargs["port"]
        self._porttype = kwargs.get("porttype", "USB")
        self._timemode = int(kwargs.get("timemode", TMODE_DISABLED))
        self._acclimit = int(kwargs.get("acclimit", DEFAULT_ACCURACY))
        self._duration = int(kwargs.get("duration", DEFAULT_DURATION))
        self._postype = int(kwargs.get("postype", POS_LLH))
        self._waittime = int(kwargs.get("waittime", WAITTIME))
        self._fixedpos = kwargs.get("fixedpos", DEFAULT_POS)
        self._ubxreader = UBXReader(
            self._stream,
            protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
        )
        self._out_queue = Queue()
        self._stop_event = Event()
        self._last_ack = datetime.now()
        self._read_thread = Thread(
            target=self._read_data,
            daemon=True,
            args=(
                stream,
                self._ubxreader,
                self._out_queue,
                self._stop_event,
            ),
        )
        self._svin_elapsed = 0
        self._msg_ack = 0
        self._msg_nak = 0
        self._msg_write = 0
        self._msg_load = 0  # if self._timemode == TMODE_DISABLED else 1
        self._msg_rtcm = 0

    def _config_svin(self, queue: Queue) -> int:
        """
        Configure Survey-In mode with specified accuracy limit.
        """

        print(
            f"Survey-in duration {self._duration}s, accuracy limit {self._acclimit}cm"
        )
        self._waittime += self._duration
        layers = 1
        transaction = 0
        acclimit = int(round(self._acclimit * 100, 0))  # mm * 10
        cfg_data = [
            ("CFG_TMODE_MODE", self._timemode),
            ("CFG_TMODE_SVIN_ACC_LIMIT", acclimit),
            ("CFG_TMODE_SVIN_MIN_DUR", self._duration),
            # (f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}", 1),
        ]
        ubx = UBXMessage.config_set(layers, transaction, cfg_data)
        queue.put(ubx)
        self._msg_load += 1
        return 1

    def _config_fixed(self, queue: Queue) -> int:
        """
        Configure Fixed mode with specified coordinates.
        """

        print(
            f"Fixed position format {('ECEF','LLH')[self._postype]}, {self._fixedpos}, "
            f"accuracy limit {self._acclimit}cm"
        )
        layers = 1
        transaction = 0
        acclimit = int(round(self._acclimit * 100, 0))  # mm * 10
        x, y, z = self._fixedpos
        if self._postype == POS_ECEF:
            x, xhp = h2sphp(x)
            y, yhp = h2sphp(y)
            z, zhp = h2sphp(z)
            cfg_data = [
                ("CFG_TMODE_MODE", self._timemode),
                ("CFG_TMODE_POS_TYPE", self._postype),
                ("CFG_TMODE_FIXED_POS_ACC", acclimit),  # mm * 10
                ("CFG_TMODE_ECEF_X", x),  # cm
                ("CFG_TMODE_ECEF_X_HP", xhp),  # mm * 10
                ("CFG_TMODE_ECEF_Y", y),  # cm
                ("CFG_TMODE_ECEF_Y_HP", yhp),  # mm * 10
                ("CFG_TMODE_ECEF_Z", z),  # cm
                ("CFG_TMODE_ECEF_Z_HP", zhp),  # mm * 10
            ]
        else:
            x, xhp = ll2sphp(x)
            y, yhp = ll2sphp(y)
            z, zhp = h2sphp(z)
            cfg_data = [
                ("CFG_TMODE_MODE", self._timemode),
                ("CFG_TMODE_POS_TYPE", self._postype),
                ("CFG_TMODE_FIXED_POS_ACC", acclimit),  # mm * 10
                ("CFG_TMODE_LAT", x),
                ("CFG_TMODE_LAT_HP", xhp),
                ("CFG_TMODE_LON", y),
                ("CFG_TMODE_LON_HP", yhp),
                ("CFG_TMODE_HEIGHT", z),  # cm
                ("CFG_TMODE_HEIGHT_HP", zhp),  # mm * 10
            ]
        ubx = UBXMessage.config_set(layers, transaction, cfg_data)
        queue.put(ubx)
        self._msg_load += 1
        return 1

    def _config_disabled(self, queue: Queue) -> int:
        """
        Configure Fixed mode with specified coordinates.
        """

        tmode = TMODE_DISABLED
        layers = 1
        transaction = 0
        cfg_data = [
            ("CFG_TMODE_MODE", tmode),
        ]
        ubx = UBXMessage.config_set(layers, transaction, cfg_data)
        queue.put(ubx)
        self._msg_load += 1
        return 1

    def _config_output(
        self, queue: Queue, rate: int = 1, port_type: str = "USB"
    ) -> int:
        """
        Configure which RTCM3 and UBX messages to output.
        """

        print(f"{('Disabling','Enabling')[rate]} output messages")
        layers = 1  # 1 = RAM, 2 = BBR, 4 = Flash (can be OR'd)
        transaction = 0
        cfg_data = (
            [(f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}", 1)]
            if self._timemode == TMODE_SVIN
            else []
        )
        for rtcm_type in (
            "1006",
            "1077",
            "1087",
            "1097",
            "1127",
            "1230",
        ):
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append([cfg, rate])

        ubx = UBXMessage.config_set(layers, transaction, cfg_data)
        queue.put(ubx)
        self._msg_load += 1
        return 1

    def _read_data(
        self,
        stream: object,
        ubr: UBXReader,
        queue: Queue,
        stop: Event,
    ):
        """
        THREADED
        Read incoming UBX and RTCM data from device.
        """
        # pylint: disable=broad-except

        # read until expected no of acknowledgements has been received
        # or waittime has been exceeded.
        while not stop.is_set():
            try:
                (_, parsed_data) = ubr.read()
                if parsed_data is not None:
                    if (
                        parsed_data.identity in (ACK, NAK)
                        and parsed_data.clsID == 6  # CFG
                        and parsed_data.msgID == 138  # CFG-VALSET
                    ):
                        self._last_ack = datetime.now()
                        if parsed_data.identity == ACK:
                            self._msg_ack += 1
                        else:
                            self._msg_nak += 1
                        self.logger.debug(
                            f"ACKNOWLEDGEMENT {self._msg_ack + self._msg_nak} - {parsed_data}"
                        )
                    if (
                        self._timemode in (TMODE_FIXED, TMODE_SVIN)
                        and parsed_data.identity == "1006"
                    ):
                        self._msg_rtcm += 1
                        self.logger.debug(
                            f"RTCM 1006 ACTIVE BASE {self._msg_rtcm} - {parsed_data}"
                        )
                    if (
                        self._timemode == TMODE_SVIN
                        and parsed_data.identity == "NAV-SVIN"
                    ):
                        self._svin_elapsed = parsed_data.dur
                        self.logger.debug(f"UBX NAV-SVIN - {parsed_data}")

                # send config message(s) to receiver
                if not queue.empty():
                    i = 0
                    while not queue.empty():
                        i += 1
                        parsed_data = queue.get()
                        self._msg_write += 1
                        self.logger.debug(
                            f"WRITE {self._msg_write} {parsed_data.identity}"
                        )
                        stream.write(parsed_data.serialize())
                        sleep(WRITETIME)
                    queue.task_done()

            except (UBXMessageError, UBXParseError):
                continue
            except Exception as err:
                if not stop.is_set():
                    print(f"Something went wrong {err}")
                continue

    def run(self):
        """
        Run configuration load routines.
        """

        rc = 0
        if self._timemode in (TMODE_FIXED, TMODE_SVIN):
            print(
                f"Configuring device at port {self._port} as base station using "
                f"{('disabled', 'survey-in', 'fixed')[self._timemode]} timing mode"
            )
        else:
            print(f"Configuring device at port {self._port} to disable base station")

        start = datetime.now()
        self._read_thread.start()
        if self._timemode == TMODE_SVIN:
            rc = self._config_svin(self._out_queue)
        elif self._timemode == TMODE_FIXED:
            rc = self._config_fixed(self._out_queue)
        else:
            rc = self._config_disabled(self._out_queue)
        if rc:
            rc = self._config_output(
                self._out_queue,
                rate=self._timemode != TMODE_DISABLED,
                port_type=self._porttype,
            )

        # loop until waittime / survey duration expired or user presses Ctrl-C
        i = 0
        while datetime.now() < start + timedelta(seconds=self._waittime):
            try:
                if self._timemode == TMODE_SVIN:
                    i = self._svin_elapsed  # from NAV-SVIN message
                    wt = self._duration
                else:
                    i += 1
                    wt = self._waittime
                progbar(i, wt, wt)
                sleep(1)
            except KeyboardInterrupt:  # capture Ctrl-C
                print("\nTerminated by user. Configuration may be incomplete.")
                break

        self._stop_event.set()
        self._read_thread.join()

        if self._msg_ack == self._msg_load and (
            (self._timemode in (TMODE_FIXED, TMODE_SVIN) and self._msg_rtcm > 1)
            or (self._timemode == TMODE_DISABLED and self._msg_rtcm == 0)
        ):
            print(
                "Configuration successful. "
                f"{self._msg_ack} configuration messages acknowledged. "
                f"{self._msg_rtcm} RTCM 1006 (active base) messages confirmed."
            )
            rc = 1
        else:
            print(
                "\nConfiguration unsuccessful. "
                f"{self._msg_load} configuration messages sent, "
                f"{self._msg_ack} acknowledged, {self._msg_nak} rejected, "
                f"{self._msg_rtcm} RTCM 1006 (active base) messages received."
            )
            if not self._msg_rtcm:
                print(
                    f"Consider increasing accuracy limit to >{self._acclimit}cm "
                    f"or increasing survey duration to >{self._duration} seconds."
                )
            if self._msg_nak:
                print("Check device supports base station configuration.")
            rc = 0

        return rc


def main():
    """
    CLI Entry point.

    :param: as per UBXBase constructor.
    """

    def duration_in_range(value):
        val = int(value)
        if not 0 < val <= 3600:
            raise ArgumentTypeError(f"{value} must be between 0 and 3600")
        return val

    def fixedpos_in_range(value):
        try:
            val = value.split(",")
            val = [float(val[i]) for i in range(len(val))]
        except (TypeError, ValueError):
            val = ()
        if len(val) != 3:
            raise ArgumentTypeError(
                f"{value} must be in format (lat,lon,height) or (X,Y,Z)"
            )
        return val

    ap = ArgumentParser(epilog=EPILOG, formatter_class=ArgumentDefaultsHelpFormatter)
    ap.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    ap.add_argument("-P", "--port", required=False, help="Serial port")
    ap.add_argument(
        "--baudrate",
        required=False,
        help="Serial baud rate",
        type=int,
        choices=[4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800],
        default=38400,
    )
    ap.add_argument(
        "--timeout",
        required=False,
        help="Serial timeout in seconds",
        type=float,
        default=3.0,
    )
    ap.add_argument(
        "--portype",
        required=False,
        help="Serial port type",
        type=str,
        choices=("USB", "UART1", "UART2", "I2C"),
        default="USB",
    )
    ap.add_argument(
        "--timemode",
        required=False,
        help=(
            f"Timing mode {TMODE_DISABLED} = disabled, "
            f"{TMODE_SVIN} = survey-in, {TMODE_FIXED} = fixed"
        ),
        type=int,
        choices=(TMODE_DISABLED, TMODE_SVIN, TMODE_FIXED),
        default=TMODE_SVIN,
    )
    ap.add_argument(
        "--acclimit",
        required=False,
        help="Accuracy limit in cm",
        type=float,
        default=DEFAULT_ACCURACY,
    )
    ap.add_argument(
        "--duration",
        required=False,
        help="Survey-In duration in seconds",
        type=duration_in_range,
        default=DEFAULT_DURATION,
    )
    ap.add_argument(
        "--postype",
        required=False,
        help=f"Position fixed reference type {POS_ECEF} = ECEF, {POS_LLH} = LLH",
        type=int,
        choices=(POS_ECEF, POS_LLH),
        default=POS_LLH,
    )
    ap.add_argument(
        "--fixedpos",
        required=False,
        help="Fixed reference position in either LLH (lat, lon, height in cm) \
            or ECEF (X, Y, Z in cm) format",
        type=fixedpos_in_range,
        default=DEFAULT_POS,
    )
    ap.add_argument(
        "--waittime",
        required=False,
        help="Response wait time in seconds",
        type=float,
        default=WAITTIME,
    )

    kwargs = set_common_args("ubxbase", ap, logdefault=VERBOSITY_HIGH)

    if kwargs.get("port", None) is None:
        raise ParameterError("Serial port must be specified")

    with Serial(
        kwargs.get("port"), kwargs.pop("baudrate"), timeout=kwargs.pop("timeout")
    ) as serial_stream:
        ubl = UBXBase(serial_stream, **kwargs)
        ubl.run()


if __name__ == "__main__":
    main()
