"""
Collection of GNSS related helper methods.

Created on 26 May 2022

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2020
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name

import logging
import logging.handlers
from argparse import ArgumentParser
from math import trunc
from os import getenv

from pyubxutils.globals import (
    LOGFORMAT,
    LOGGING_LEVELS,
    LOGLIMIT,
    VERBOSITY_CRITICAL,
    VERBOSITY_DEBUG,
    VERBOSITY_HIGH,
    VERBOSITY_LOW,
    VERBOSITY_MEDIUM,
)


def parse_config(configfile: str) -> dict:
    """
    Parse config file.

    :param str configfile: fully qualified path to config file
    :returns: config as kwargs, or None if file not found
    :rtype: dict
    :raises: FileNotFoundError
    :raises: ValueError
    """

    config = {}
    try:
        with open(configfile, "r", encoding="utf-8") as infile:
            for cf in infile:
                if cf[0] != "#":  # comment
                    key, val = cf.split("=", 1)
                    config[key.strip()] = val.strip()
        return config
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Configuration file not found: {configfile}") from err
    except ValueError as err:
        raise ValueError(f"Configuration file invalid: {configfile}, {err}") from err


def set_common_args(
    name: str,
    ap: ArgumentParser,
    logname: str = "pyubxutils",
    logdefault: int = VERBOSITY_MEDIUM,
) -> dict:
    """
    Set common argument parser and logging args.

    :param str name: name of CLI utility e.g. "gnssstreamer"
    :param ArgumentParserap: argument parser instance
    :param str logname: logger name
    :param int logdefault: default logger verbosity level
    :returns: parsed arguments as kwargs
    :rtype: dict
    """

    ap.add_argument(
        "-C",
        "--config",
        required=False,
        help=(
            "Fully qualified path to CLI configuration file "
            f"(will use environment variable {name.upper()}_CONF where set)"
        ),
        default=getenv(f"{name.upper()}_CONF", None),
    )
    ap.add_argument(
        "--verbosity",
        required=False,
        help=(
            f"Log message verbosity "
            f"{VERBOSITY_CRITICAL} = critical, "
            f"{VERBOSITY_LOW} = low (error), "
            f"{VERBOSITY_MEDIUM} = medium (warning), "
            f"{VERBOSITY_HIGH} = high (info), {VERBOSITY_DEBUG} = debug"
        ),
        type=int,
        choices=[
            VERBOSITY_CRITICAL,
            VERBOSITY_LOW,
            VERBOSITY_MEDIUM,
            VERBOSITY_HIGH,
            VERBOSITY_DEBUG,
        ],
        default=logdefault,
    )
    ap.add_argument(
        "--logtofile",
        required=False,
        help="fully qualified log file name, or '' for no log file",
        type=str,
        default="",
    )

    kwargs = vars(ap.parse_args())
    # config file settings will supplement CLI and default args
    cfg = kwargs.pop("config", None)
    if cfg is not None:
        kwargs = {**kwargs, **parse_config(cfg)}

    logger = logging.getLogger(logname)
    set_logging(
        logger, kwargs.get("verbosity", logdefault), kwargs.get("logtofile", "")
    )

    return kwargs


def set_logging(
    logger: logging.Logger,
    verbosity: int = VERBOSITY_MEDIUM,
    logtofile: str = "",
    logform: str = LOGFORMAT,
    limit: int = LOGLIMIT,
):
    """
    Set logging format and level.

    :param logging.Logger logger: module log handler
    :param int verbosity: verbosity level -1,0,1,2,3 (2 - MEDIUM)
    :param str logtofile: fully qualified log file name ("")
    :param str logform: logging format (datetime - level - name)
    :param int limit: maximum logfile size in bytes (10MB)
    """

    try:
        level = LOGGING_LEVELS[int(verbosity)]
    except (KeyError, ValueError):
        level = logging.WARNING

    logger.setLevel(logging.DEBUG)
    logformat = logging.Formatter(
        logform,
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )
    if logtofile == "":
        loghandler = logging.StreamHandler()
    else:
        loghandler = logging.handlers.RotatingFileHandler(
            logtofile, mode="a", maxBytes=limit, backupCount=10, encoding="utf-8"
        )
    loghandler.setFormatter(logformat)
    loghandler.setLevel(level)
    logger.addHandler(loghandler)


def progbar(i: int, lim: int, inc: int = 50):
    """
    Display progress bar on console.
    """

    i = min(i, lim)
    pct = int(i * inc / lim)
    if not i % int(lim / inc):
        print(
            f"{int(pct*100/inc):02}% " + "\u2593" * pct + "\u2591" * (inc - pct),
            end="\r",
        )


def h2sphp(val: float) -> tuple:
    """
    Split height in cm into standard (cm) and high (mm * 10)
    precision components.

    e.g. 123456.78 -> 123456, 78

    :param val: decimal lat/lon value
    :return: tuple of integers
    :rtype: tuple
    """

    sp = trunc(val)
    hp = int(round((val - sp) * 100, 0))
    return sp, hp


def ll2sphp(val: float) -> tuple:
    """
    Split lat/lon into standard (1-7 dp) and high (8-9 dp)
    precision components.

    e.g. 51.123456789 -> 511234567, 89

    :param val: decimal height value in cm
    :return: tuple of integers
    :rtype: tuple
    """

    return h2sphp(val * 1e7)
