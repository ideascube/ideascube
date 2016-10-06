from django.core.management import call_command

import pytest

from ideascube.configuration import get_config
from ideascube.serveradmin.catalog import Package


@pytest.mark.usefixtures('db', 'systemuser')
def test_reset_home_to_installed_packages(catalog):
    catalog.add_mocked_package(Package('pkg1', {
        'name':'Test package1',
        'description':'Test package1 description',
        'language':'fr',
        'staff_only':False,
    }))
    catalog.add_mocked_package(Package('pkg2', {
        'name':'Test package2',
        'description':'Test package2 description',
        'language':'fr',
        'staff_only':False,
    }))
    assert get_config('home-page', 'displayed-package-ids') == []

    call_command('reset_home')
    assert get_config('home-page', 'displayed-package-ids') == ['pkg1', 'pkg2']


@pytest.mark.usefixtures('db', 'systemuser')
def test_reset_home_no_installed_packages():
    assert get_config('home-page', 'displayed-package-ids') == []

    call_command('reset_home')
    assert get_config('home-page', 'displayed-package-ids') == []
