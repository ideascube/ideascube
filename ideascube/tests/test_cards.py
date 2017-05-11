def test_build_builtin_card_info(settings):
    from ideascube.cards import build_builtin_card_info

    settings.BUILTIN_APP_CARDS = ['foo', 'bar']
    assert build_builtin_card_info() == [{'id': 'foo'}, {'id': 'bar'}]


def test_build_extra_app_card_info(settings):
    from ideascube.cards import build_extra_app_card_info

    settings.EXTRA_APP_CARDS = ['foo', 'bar']
    assert build_extra_app_card_info() == [{'id': 'foo'}, {'id': 'bar'}]


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

    assert build_package_card_info() == [{
        'package_id' : 'test.package1.fr',
        'name'       : 'Test package1',
        'description': 'Test package1 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'kiwix',
        'css_class'  : 'test.package1',
        'theme'      : 'learn'
    },
    {
        'package_id' : 'test.package2.fr',
        'name'       : 'Test package2',
        'description': 'Test package2 description',
        'lang'       : 'fr',
        'is_staff'   : False,
        'id'         : 'media-package',
        'css_class'  : None,
        'theme'      : None
    }]
