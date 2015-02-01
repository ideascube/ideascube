import pytest

from ..backup import Backup

DATA_ROOT = 'serveradmin/tests/data'


@pytest.fixture
def backup(monkeypatch):
    monkeypatch.setattr('serveradmin.backup.Backup.ROOT', DATA_ROOT)
    # ZIP file should be shipped by git in serveradmin/tests/data
    return Backup('musasa_0.1.0_201501241620.zip')
