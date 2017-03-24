import glob
import os
import importlib

import pytest


@pytest.fixture(params=sorted([
    f for f in glob.glob('ideascube/conf/*.py')
    if not f.endswith('/__init__.py')
]))
def setting_module(request):
    basename = os.path.basename(request.param)

    module, _ = os.path.splitext(basename)
    return '.conf.%s' % module


def test_setting_file(setting_module):
    from ideascube.forms import UserImportForm

    settings = importlib.import_module(setting_module, package="ideascube")

    assert isinstance(getattr(settings, 'IDEASCUBE_NAME', ''), str)

    for name, _ in getattr(settings, 'USER_IMPORT_FORMATS', []):
        assert hasattr(UserImportForm, '_get_{}_mapping'.format(name))
        assert hasattr(UserImportForm, '_get_{}_reader'.format(name))
