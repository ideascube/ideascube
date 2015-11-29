import pytest

from ..wifi import WPAConfig
from ..backup import Backup

DATA_ROOT = 'ideascube/serveradmin/tests/data'


@pytest.fixture
def backup(monkeypatch):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    # ZIP file should be shipped by git in serveradmin/tests/data
    return Backup('musasa-0.1.0-201501241620.zip')


@pytest.fixture
def wpa_config(request):
    path = WPAConfig.configfile
    WPAConfig.configfile = '/tmp/hostapd.conf'

    with open(WPAConfig.configfile, 'w') as fd:
        fd.write('''
# some comment
wpa = 2
wpa_passphrase = pwa
wpa_key_mgmt = WPA-PSK
rsn_pairwise = CCMP
        ''')

    def fin():
        WPAConfig.configfile = path

    request.addfinalizer(fin)
    return WPAConfig()
