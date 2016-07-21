import pytest
import os

from ..backup import Backup

DATA_ROOT = 'ideascube/serveradmin/tests/data/backup'
BACKUPS_ROOT = 'ideascube/serveradmin/tests/backups'


@pytest.fixture
def backup_root(request):
    os.makedirs(BACKUPS_ROOT, exist_ok=True)
    def fin():
        os.rmdir(BACKUPS_ROOT)
    request.addfinalizer(fin)


@pytest.fixture
def backup(monkeypatch):
    monkeypatch.setattr('ideascube.serveradmin.backup.Backup.ROOT', DATA_ROOT)
    # ZIP file should be shipped by git in serveradmin/tests/data
    return Backup('musasa-0.1.0-201501241620.tar.gz')


@pytest.fixture
def package_path(tmpdir):
    return os.path.join(str(tmpdir), "test_package.zip")


@pytest.yield_fixture()
def csv_writer():
    CSV_PATH = os.path.join(os.path.dirname(__file__), 'data/metadata.csv')

    def write_metadata(metadata):
        with open(CSV_PATH, 'w') as f:
            f.write(metadata)
        return CSV_PATH

    yield write_metadata

    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)