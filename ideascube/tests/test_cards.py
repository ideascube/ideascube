import pytest
from ideascube.mediacenter.tests.factories import DocumentFactory

def test_build_builtin_card_info(settings):
    from ideascube.cards import build_builtin_card_info

    settings.BUILTIN_APP_CARDS = ['library', 'mediacenter']
    assert build_builtin_card_info() == [
        {'id': 'library'}, {'id': 'mediacenter'}
    ]


def test_build_extra_app_card_info(settings):
    from ideascube.cards import build_extra_app_card_info

    settings.EXTRA_APP_CARDS = ['bsfcampus', 'koombookedu']
    assert build_extra_app_card_info() == [
        {'id': 'bsfcampus'}, {'id': 'koombookedu'}
    ]


def test_build_package_card_info_must_not_fail_for_no_package(systemuser):
    from ideascube.configuration import set_config
    from ideascube.cards import build_package_card_info
    set_config('home-page', 'displayed-package-ids', ['test.package1'], systemuser)
    assert build_package_card_info() == []


def test_build_package_card_info(systemuser, catalog):
    from ideascube.configuration import set_config
    from ideascube.cards import build_package_card_info
    from ideascube.serveradmin.catalog import ZippedZim, ZippedMedias
    catalog.add_mocked_package(ZippedZim('test.package1.fr', {
        'name':'Test package1',
        'description':'Test package1 description',
        'language':'fr',
        'staff_only':False}))
    catalog.add_mocked_package(ZippedMedias('test.package2.fr', {
        'name':'Test package2',
        'description':'Test package2 description',
        'language':'fr',
        'staff_only':False}))
    set_config('home-page', 'displayed-package-ids', ['test.package1.fr', 'test.package2.fr'], systemuser)
    thumbnail = DocumentFactory(title='__package_test.package2.fr_thumbnail__')

    assert build_package_card_info() == [{
        'package_id' : 'test.package1.fr',
        'name'       : 'Test package1',
        'description': 'Test package1 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'kiwix',
        'css_class'  : 'test.package1',
        'theme'      : 'learn',
        'icon_document': None,
    },
    {
        'package_id' : 'test.package2.fr',
        'name'       : 'Test package2',
        'description': 'Test package2 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'media-package',
        'css_class'  : 'mediacenter',
        'theme'      : 'discover',
        'icon_document'  : thumbnail,
    }]
