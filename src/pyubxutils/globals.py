"""
Global variables for pyubxutils.

Created on 26 May 2022

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2022
:license: BSD 3-Clause
"""

CLIAPP = "CLI"
EARTH_RADIUS = 6371  # km
"""Earth radius in km"""

# ranges for ubxsetrate CLI
ALLNMEA = "allnmea"
ALLUBX = "allubx"
EPILOG = (
    "© 2022 SEMU Consulting BSD 3-Clause license"
    " - https://github.com/semuconsulting/pyubxutils/"
)
"""CLI argument parser epilog"""
MINNMEA = "minnmea"
MINUBX = "minubx"
ALLNMEA_CLS = [b"\xf0", b"\xf1"]
MINMMEA_ID = [b"\xf0\x00", b"\xf0\x02", b"\xf0\x03", b"\xf0\x04", b"\xf0\x05"]
ALLUBX_CLS = [b"\x01"]
MINUBX_ID = [b"\x01\x04", b"\x01\x07", b"\x01\x35"]
TTY_PROTOCOL = 32

VERBOSITY_CRITICAL = -1
"""Verbosity critical"""
VERBOSITY_LOW = 0
"""Verbosity error"""
VERBOSITY_MEDIUM = 1
"""Verbosity warning"""
VERBOSITY_HIGH = 2
"""Verbosity info"""
VERBOSITY_DEBUG = 3
"""Verbosity debug"""

LOGFORMAT = "{asctime}.{msecs:.0f} - {levelname} - {name} - {message}"
"""Logging format"""
LOGLIMIT = 10485760  # max size of logfile in bytes
"""Logfile limit"""

LOGGING_LEVELS = {
    VERBOSITY_CRITICAL: "CRITICAL",
    VERBOSITY_LOW: "ERROR",
    VERBOSITY_MEDIUM: "WARNING",
    VERBOSITY_HIGH: "INFO",
    VERBOSITY_DEBUG: "DEBUG",
}

UBXSIMULATOR = "UBXSIMULATOR"
"""UBX simulator"""
