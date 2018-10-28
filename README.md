# upy_ota
Micropython Ota: server, firmware


##Server OTA: 
Use aiohttp with StreamResponse:

##Firmware with OTA:
Inside FTP server for first upload files.

```python
import network
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("Wifi", "pwd")

import ftp.ftp as ftp
ftp.ftpserver()
'''
