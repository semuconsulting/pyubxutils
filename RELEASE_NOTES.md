# pyubxutils Release Notes

### RELEASE 1.0.5

FIXES:

1. Restore command line scripts. Fixes #8.

### RELEASE 1.0.4

ENHANCEMENTS:

1. Drop active support for Python 3.9, add Python 3.14.

### RELEASE 1.0.3

ENHANCEMENTS:

1. UBXSimulator now supports limited TTY (AT+) commands. `AT+ECHO=OK` and `AT+ECHO=Error` commands will simulate an `OK` or `Error` TTY response. An `AT+ECHO=xxxxxx` command will echo back the `xxxxxx` string.

### RELEASE 1.0.2

FIXES:

1. Fix typo in ubxbase config. 

### RELEASE 1.0.1

ENHANCEMENTS:

1. Add `ubxbase` utility to configure compatible u-blox receiver (e.g. ZED-F9P) to Base Station mode. Type `ubxbase -h` for help.

### RELEASE 1.0.0

CHANGES:

1. Move UBX CLI utilities from pygnssutils to new library pyubxutils.

