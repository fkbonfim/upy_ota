# upy_ota
Micropython Ota: server, firmware


## Server OTA: 
Use aiohttp with StreamResponse:

## Firmware with OTA:
Inside FTP server for first upload files.

```python
import network
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("Wifi", "pwd")

import ftp.ftp as ftp
ftp.ftpserver()
```


Some video:

[Try change partition](https://youtu.be/fImFlty40GY).
[Test OTA server](https://www.youtube.com/watch?v=_ywJw2IqUIYY).

