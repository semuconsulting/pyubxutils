pyubxutils
=======

[Current Status](#currentstatus) |
[Installation](#installation) |
[ubxsimulator](#ubxsimulator) |
[ubxsave CLI](#ubxsave) |
[ubxload CLI](#ubxload) |
[ubxbase CLI](#ubxbase) |
[ubxsetrate CLI](#ubxsetrate) |
[ubxcompare CLI](#ubxcompare) |
[Graphical Client](#gui) |
[Author & License](#author)

pyubxutils is an original series of Python u-blox ™ UBX © protocol utility classes and CLI tools built around the following core libraries from the same stable:

- [pyubx2](https://github.com/semuconsulting/pyubx2) - UBX parsing and generation library

1. [`ubxsimulator`](#ubxsimulator) utility. This provides a basic simulation of a GNSS receiver serial stream by generating synthetic UBX or NMEA messages based on parameters defined in a json configuration file.
1. [`ubxsave`](#ubxsave) CLI utility. This saves a complete set of configuration data from any Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P) to a file. The file can then be reloaded to any compatible device using the `ubxload` utility.
1. [`ubxload`](#ubxload) CLI utility. This reads a file containing binary configuration data and loads it into any compatible Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P).
1. [`ubxbase`](#ubxbase) CLI utility. A utility which configures compatible u-blox GNSS receivers (e.g. ZED-F9P) as RTK base stations, using either Fixed or Survey-In timing modes.
1. [`ubxsetrate`](#ubxsetrate) CLI utility. A simple utility which sets NMEA or UBX message rates on u-blox GNSS receivers.
1. [`ubxcompare`](#ubxcompare) CLI utility. Utility for comparing two or more u-blox config files in either text (\*.txt) or binary (\*.ubx) format. Output files from the `ubxsave` utility can be used as input files.

The pyubxutils homepage is located at [https://github.com/semuconsulting/pyubxutils](https://github.com/semuconsulting/pyubxutils).

**This is an independent project and we have no affiliation whatsoever with u-blox**.

## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/pyubxutils)
![Release](https://img.shields.io/github/v/release/semuconsulting/pyubxutils?include_prereleases)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/pyubxutils/main.yml?branch=main)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyubxutils)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyubxutils)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyubxutils.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyubxutils)

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyubxutils](https://www.semuconsulting.com/pyubxutils).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyubxutils/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/pyubxutils/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyubxutils/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided. For general queries and advice, post a message to one of the [pyubxutils Discussions](https://github.com/semuconsulting/pyubxutils/discussions) channels.

---
## <a name="installation">Installation</a>

![Python version](https://img.shields.io/pypi/pyversions/pyubxutils.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyubxutils.svg?style=flat)](https://pypi.org/project/pyubxutils/)
[![PyPI downloads](https://github.com/semuconsulting/pygpsclient/blob/master/images/clickpy_icon.svg?raw=true)](https://clickpy.clickhouse.com/dashboard/pyubxutils)

`pyubxutils` is compatible with Python >= 3.10. In the following, `python3` & `pip` refer to the Python 3 executables. You may need to substitute `python` for `python3`, depending on your particular environment (*on Windows it's generally `python`*). **It is strongly recommended that** the Python 3 binaries (\Scripts or /bin) and site_packages directories are included in your PATH (*most standard Python 3 installation packages will do this automatically if you select the 'Add to PATH' option during installation*).

The recommended way to install the latest version of `pyubxutils` is with [pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pyubxutils
```

If required, `pyubxutils` can also be installed into a virtual environment, e.g.:

```shell
python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv env
source env/bin/activate (or env\Scripts\activate on Windows)
python3 -m pip install --upgrade pyubxutils
...
deactivate
```

For [Conda](https://docs.conda.io/en/latest/) users, `pyubxutils` is also available from [conda forge](https://github.com/conda-forge/pyubxutils-feedstock):

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyubxutils/badges/version.svg)](https://anaconda.org/conda-forge/pyubxutils)
[![Anaconda-Server Badge](https://img.shields.io/conda/dn/conda-forge/pyubxutils)](https://anaconda.org/conda-forge/pyubxutils)

```shell
conda install -c conda-forge pyubxutils
```

---
## <a name="ubxsimulator">ubxsimulator utility</a>

### EXPERIMENTAL

Provides a simple simulation of a GNSS serial stream by generating synthetic UBX or NMEA messages based on parameters defined in a json configuration file. Can simulate a motion vector based on a specified course over ground and speed. Location of configuration file can be set via environment variable `UBXSIMULATOR`.

Example usage:

```shell
ubxsimulator --simconfigfile "/home/myuser/ubxsimulator.json" --interval 1000 --timeout 3 --verbosity 3
```

```python
from os import getenv
from pyubxutils import UBXSimulator, UBXSIMULATOR
from pyubx2 import UBXReader

with UBXSimulator(
    configfile=getenv(UBXSIMULATOR, "/home/myuser/ubxsimulator.json"),
    interval=1000,
    timeout=3,
) as stream:
    ubr = UBXReader(stream)
    for raw, parsed in ubr:
        print(parsed)
```

Generates mock acknowledgements (ACK-ACK) for valid incoming UBX or TTY (AT+) commands and polls.

See sample [ubxsimulator.json](https://github.com/semuconsulting/pyubxutils/blob/main/examples/ubxsimulator.json) configuration file in the \examples folder, and the [Sphinx API documentation](https://www.semuconsulting.com/pyubxutils/pyubxutils.html#module-pyubxutils.ubxsimulator).

**NB:** Principally intended for testing Python GNSS application functionality. There is currently no attempt to simulate real-world satellite geodetics, though this could be done using e.g. the Python [`skyfield`](https://pypi.org/project/skyfield/) library and the  relevant satellite [TLE (orbital elements) data](https://celestrak.org/NORAD/elements/table.php?GROUP=gnss&FORMAT=tle). We may look into adding such functionality as and when time permits. Contributions welcome.

Command line arguments can be stored in a configuration file and invoked using the `-C` or `--config` argument. The location of the configuration file can be set in environment variable `UBXSIMULATOR_CONF`.

---
## <a name="ubxsave">ubxsave CLI</a>

*GENERATION 9+ DEVICES ONLY (e.g. NEO-M9N or ZED-F9P)*

```
class pyubxutils.ubxsave.UBXSaver(file, stream, **kwargs)
```

CLI utility which saves Generation 9+ UBX device configuration data to a file. `ubxsave` polls configuration data via the device's serial port using a series of CFG-VALGET poll messages. It parses the responses to these polls, converts them to CFG-VALSET command messages and saves these to a binary file. This binary file can then be loaded into any compatible UBX device (e.g. via the `ubxload` utility) to restore the saved configuration.

The CFG-VALSET commands are stored as a single transaction. If one or more fails on reload, the entire set will be rejected.

*NB*: The utility relies on receiving a complete set of poll responses within a specified `waittime`. If the device is exceptionally busy or the transmit buffer is full, poll responses may be delayed or dropped altogether. If the utility reports errors, try increasing the waittime. 

### CLI Usage:

```shell
ubxsave --port /dev/ttyACM1 --baudrate 9600 --timeout 0.02 --outfile ubxconfig.ubx --verbosity 1
```

For help and full list of optional arguments, type:

```shell
ubxsave -h
```

---
## <a name="ubxload">ubxload CLI</a>

*GENERATION 9+ DEVICES ONLY (e.g. NEO-M9N or ZED-F9P)*

```
class pyubxutils.ubxload.UBXLoader(file, stream, **kwargs)
```

CLI utility which loads UBX configuration (CFG-VALSET) data from a binary file (e.g. one created by the `ubxsave` utility) and loads it into the volatile memory (RAM) of a compatible Generation 9+ UBX device via its serial port. It then awaits acknowledgements to this data and reports any errors.

### CLI Usage:

```shell
ubxload --port /dev/ttyACM1 --baudrate 9600 --timeout 0.05 --infile ubxconfig.ubx --verbosity 1
```

For help and full list of optional arguments, type:

```shell
ubxload -h
```

---
## <a name="ubxbase">ubxbase CLI</a>

*RTK-COMPATIBLE GENERATION 9+ DEVICES ONLY (e.g. ZED-F9P)*

```
class pyubxutils.ubxbase.UBXBase(file, stream, **kwargs)
```

CLI utility which configures a compatible u-blox receiver to RTK base station mode, using either Fixed or Survey-In timing modes.

### CLI Usage:

```shell
ubxbase -P /dev/ttyACM0 --timemode 2 --fixedpos 37.2334512,-115.8151357,18226.4 --postype 1 --acclimit 10 --waittime 5
```

For help and full list of optional arguments, type:

```shell
ubxbase -h
```

---
## <a name="ubxsetrate">ubxsetrate CLI</a>

```
class pyubxutils.ubxsetrate.UBXSetRate(**kwargs)
```

A simple CLI utility to set NMEA or UBX message rates on u-blox receivers via a serial port.

### CLI Usage:

Assuming the Python 3 scripts (bin) directory is in your PATH, the CLI utility may be invoked from the shell thus:

This example sets the UBX NAV-HPPOSLLH message rate to 1:

```shell
ubxsetrate --port /dev/ttyACM0 --baudrate 38400 --msgClass 0x01 --msgID 0x14 --rate 1
```
```
Opening serial port /dev/ttyACM0 @ 38400 baud...

Sending configuration message <UBX(CFG-MSG, msgClass=NAV, msgID=NAV-HPPOSLLH, rateDDC=1, rateUART1=1, rateUART2=1, rateUSB=1, rateSPI=1, reserved=0)>...

Configuration message sent.
```

Refer to [pyubx2 documentation](https://github.com/semuconsulting/pyubx2/blob/master/pyubx2/ubxtypes_core.py) for available `msgClass` and `msgID` values. `msgClass` and `msgID` can be specified in either integer or hexadecimal formats.

Alternatively, the `msgClass` keyword can be set to one of the following group values (in which case the `msgID` keyword can be omitted):
- "allubx" - set rate for all available UBX NAV messages
- "minubx" - set rate for a minimum set of UBX NAV messages (NAV-PVT, NAV-SAT)
- "allnmea" - set rate for all available NMEA messages
- "minnmea" - set rate for a minimum set of NMEA messages (GGA, GSA, GSV, RMC, VTG)

For help and full list of optional arguments, type:

```shell
ubxsetrate -h
```

---
## <a name="ubxcompare">ubxcompare CLI</a>

```
class pyubxutils.ubxcompare.UBXCompare(infiles, form, diffsonly)
```

A simple CLI utility for comparing the contents of two or more u-blox configuration files. Files can be in text (\*.txt) format (as used by u-center or ArduSimple) or binary (\*.ubx) format (as used by [PyGPSClient](https://github.com/semuconsulting/PyGPSClient) or [ubxsave](#ubxsave)).

e.g. 

```shell
ubxcompare --infiles "simpleRTK2B_FW132_Rover_1Hz-00.txt, simpleRTK2B_FW132_Rover_10Hz-00.txt" --format 0 --diffsonly 1
```
```
24 configuration commands processed in simpleRTK2B_FW132_Rover_1Hz-00.txt

24 configuration commands processed in simpleRTK2B_FW132_Rover_10Hz-00.txt

2 files processed, list of differences in config keys and their values follows:

CFG_MSGOUT_NMEA_ID_GSA_UART1 (DIFFS!): {1: '1', 2: '0'}
CFG_MSGOUT_NMEA_ID_GSA_UART2 (DIFFS!): {1: '1', 2: '0'}
CFG_MSGOUT_NMEA_ID_GSV_UART1 (DIFFS!): {1: '1', 2: '0'}
CFG_MSGOUT_NMEA_ID_GSV_UART2 (DIFFS!): {1: '1', 2: '0'}
CFG_RATE_MEAS (DIFFS!): {1: '1000', 2: '100'}

Total config keys: 1475. Total differences: 5.
```

For help and full list of optional arguments, type:

```shell
ubxcompare -h
```

---
## <a name="author">Author & License Information</a>

semuadmin@semuconsulting.com

![License](https://img.shields.io/github/license/semuconsulting/pyubxutils.svg)

`pyubxutils` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, please consider sponsoring the project with the price of a coffee...

[![Sponsor](https://github.com/semuconsulting/pyubx2/blob/master/images/sponsor.png?raw=true)](https://buymeacoffee.com/semuconsulting)
