import importlib

import pytest


def test_all_settings(request):
    confdir = request.fspath.dirpath().dirpath().join('conf')
    assert confdir.check(dir=True)

    for path in confdir.listdir():
        if path.ext != '.py':
            continue

        module = path.purebasename
        module = '.conf.%s' % module

        settings = importlib.import_module(module, package="ideascube")

        assert isinstance(getattr(settings, 'IDEASCUBE_NAME', ''), str)
