import glob
import os
import importlib

import pytest


@pytest.fixture(params=glob.glob('ideascube/conf/*.py'))
def setting_module(request):
    basename = os.path.basename(request.param)

    module, _ = os.path.splitext(basename)
    return '.conf.%s' % module


def test_setting_file(setting_module):
    settings = importlib.import_module(setting_module, package="ideascube")

    assert isinstance(getattr(settings, 'IDEASCUBE_NAME', ''), str)
