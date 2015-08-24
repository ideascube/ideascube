import pytest
from django.utils.translation import ugettext as _

from ..backup import Backup

DATA_ROOT = 'ideasbox/serveradmin/tests/data'
try:
    from io import StringIO
except ImportError:  # Python < 3
    from StringIO import StringIO


@pytest.fixture
def backup(monkeypatch):
    monkeypatch.setattr('ideasbox.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    # ZIP file should be shipped by git in serveradmin/tests/data
    return Backup('musasa_0.1.0_201501241620.zip')

@pytest.fixture
def list_output():
    bsf01 = """wlan0     Scan completed :
          Cell 01 - Address: 70:62:B8:52:79:B0
                    Channel:6
                    Frequency:2.437 GHz (Channel 6)
                    Quality=54/70  Signal level=-56 dBm  
                    Encryption key:on
                    ESSID:"bsf01"
                    Bit Rates:1 Mb/s; 2 Mb/s; 5.5 Mb/s; 11 Mb/s; 6 Mb/s
                              9 Mb/s; 12 Mb/s; 18 Mb/s
                    Bit Rates:24 Mb/s; 36 Mb/s; 48 Mb/s; 54 Mb/s
                    Mode:Master
                    Extra:tsf=00000000040448fe
                    Extra: Last beacon: 40ms ago
                    IE: Unknown: 0003627366
                    IE: Unknown: 010882848B960C121824
                    IE: Unknown: 030106
                    IE: Unknown: 0706474220010D14
                    IE: Unknown: 2A0100
                    IE: Unknown: 32043048606C
                    IE: Unknown: 2D1AAD0103FFFF0000000000000000000001000000000406E6A70C00
                    IE: Unknown: 3D1606000500000000000000000000000000000000000000
                    IE: Unknown: 4A0E14000A002C01C800140005001900
                    IE: Unknown: 7F080100000000000040
                    IE: Unknown: DD180050F2020101800003A4000027A4000042435E0062322F00
                    IE: Unknown: DD0900037F01010000FF7F
                    IE: IEEE 802.11i/WPA2 Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (2) : CCMP TKIP
                        Authentication Suites (1) : PSK
"""
    
    bsf02 = """Cell 02 - Address: 
                    ESSID:"bsf02"
                    Protocol:IEEE 802.11bg
                    Mode:Master
                    Frequency:2.457 GHz (Channel 10)
                    Encryption key:on
                    Bit Rates:54 Mb/s
                    Extra:wpa_ie=dd160050f20101000050f20201000050f20201000050f202
                    IE: WPA Version 1
                        Group Cipher : TKIP
                        Pairwise Ciphers (1) : TKIP
                        Authentication Suites (1) : PSK
                    Quality=100/100  Signal level=74/100
"""
    return '\n'.join([bsf01, bsf02])

