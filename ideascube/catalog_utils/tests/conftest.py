import os
import pytest


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
