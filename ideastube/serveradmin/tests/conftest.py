import pytest

from ..backup import Backup

DATA_ROOT = 'ideastube/serveradmin/tests/data'


@pytest.fixture
def backup(monkeypatch):
    monkeypatch.setattr('ideastube.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    # ZIP file should be shipped by git in serveradmin/tests/data
    return Backup('musasa-0.1.0-201501241620.zip')
