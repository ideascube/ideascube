import pytest

from ..backup import Backup

DATA_ROOT = 'ideasbox/serveradmin/tests/data'
try:
    from io import StringIO
except ImportError:  # Python < 3
    from StringIO import StringIO
from mock import patch
from django.utils.translation import ugettext as _
from wifi.utils import get_property, set_properties


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
    output = '\n'.join([bsf01, bsf02])
    return output

@pytest.fixture
def success_output():
    SUCCESSFUL_IFUP_OUTPUT = """Internet Systems Consortium DHCP Client 4.2.4
Copyright 2004-2012 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/
Listening on LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   Socket/fallback
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 4
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 8
DHCPREQUEST on wlan0 to 255.255.255.255 port 67
DHCPOFFER from 192.168.1.1
DHCPACK from 192.168.1.1
bound to 192.168.1.113 -- renewal in 2776 seconds.
"""
    return SUCCESSFUL_IFUP_OUTPUT

@pytest.fixture
def failure_output():
    FAILED_IFUP_OUTPUT = """Internet Systems Consortium DHCP Client 4.2.4
Copyright 2004-2012 Internet Systems Consortium.
All rights reserved.
For info, please visit https://www.isc.org/software/dhcp/
Listening on LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   LPF/wlan0/9c:4e:36:5d:2c:64
Sending on   Socket/fallback
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 5
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 8
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 18
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 18
DHCPDISCOVER on wlan0 to 255.255.255.255 port 67 interval 12
No DHCPOFFERS received.
No working leases in persistent database - sleeping.
"""
    return FAILED_IFUP_OUTPUT

@pytest.fixture
def disconnected_output():
    disconnected_output = """test-interface00     IEEE 802.11bgn  ESSID:off/any  
          Mode:Managed  Access Point: Not-Associated   Tx-Power=20 dBm   
          Retry short limit:7   RTS thr=2347 B   Fragment thr:off
          Power Management:off
"""
    return disconnected_output

class MyStringIO(StringIO):
# extends StringIO buit-in class to override write and close methods
# for testing IO operations.

    def __init__(self, string):
        super(MyStringIO, self).__init__(string.decode('unicode-escape'))
        self.truncate = False
    
    def write(self, string):
        if self.truncate:
            self.__init__(string)
        else:
            value = self.getvalue() + string
            self.__init__(value)
    
    def close(self):
        self.truncate = True
        self.seek(0)

@pytest.fixture
def properties_file():
    content = """scheme_current=test-scheme
    interface_current=test-interface
    scheme_active=True
    """
    properties_file = MyStringIO(content)
    return properties_file


def getproperty(prop, _file=None):
    #from wifi.utils import get_property
    # to ensure we only patch within this function execution
    with patch('__builtin__.open', return_value=_file):
        return get_property(prop)


def setproperties(interface_current=None, scheme_current=None, config=None, _file=None):
    #from wifi.utils import set_properties
    with patch('__builtin__.open', return_value=_file):
        set_properties(interface_current, scheme_current, config)


def adminset(interface_current=None, scheme_current=None, scheme_active=False, _file=None):
    # arbitrary set of the running configfile
    # does not verify coherence of the arguments
    properties = {'interface_current' : interface_current,
                  'scheme_current' : scheme_current,
                  'scheme_active' : scheme_active}
    _file.truncate = True
    for prop in properties:
        prop_line = str(prop) + '=' + str(properties[prop]) + '\n'
        _file.write(prop_line)
    _file.close()


def set_hotspots(hotspots, active=-1, connected=False, _file=None, interface=None):
    if active >= 0:
        id_ = '--'.join([hotspots[active].ssid, hotspots[active].address])
        kwargs = {'scheme_current' : id_,
        'scheme_active' : connected,
        'interface_current' : interface,
        '_file' : _file}
        adminset(**kwargs)


#def do_nothing():
#    pass

