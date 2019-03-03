# ax25lib
Python module for AX25 used in hamradio. Currently for TNC you can use Direwolf or SoundModem by UZ7HO. Example use you can see in aprs.py file.

Requirements:
Python: 2.7 (not tested on version 3)

Python modules:
- socket
- struct
- binascii
- string
- re
- datetime
- threading
- time

This is initial version that understand only UI frames (used in APRS). In future i'll try to implement full AX25 stack.

# ax25lib parameters
- type="tcp" - connection type, for now tcp only, in feature also serial
- host="192.168.0.55" - hostname or IP with running direwolf or soundmodem (mode KISS TNC)
- port=8001 - tcp port of kiss tnc
- callback=dane - run this user function when data appears.

Function declared in variable callback receives array:
- dane['source'] - source callsign
- dane['destination'] - destination callsign
- dane['via'] - via path
- dane['data'] - data in packet
- dane['control'] - control byte
- dane['pid'] - pid byte

# Contact
You can contact me via e-mail sq5t at sq5t dot com
