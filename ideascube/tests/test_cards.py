def test_build_builtin_card_info(settings):
    from ideascube.cards import build_builtin_card_info

    settings.BUILTIN_APP_CARDS = ['library', 'mediacenter']

    cards = build_builtin_card_info()
    assert len(cards) == 2

    library = cards[0]
    assert library.id == 'library'
    assert library.name == 'Library'
    assert library.description == 'Browse books.'
    assert library.category.name == 'read'
    assert library.template == 'ideascube/includes/cards/builtin.html'
    assert library.url == 'library:index'
    assert library.css_class == 'library'

    mediacenter = cards[1]
    assert mediacenter.id == 'mediacenter'
    assert mediacenter.name == 'Medias center'
    assert mediacenter.description == 'Browse videos, sounds, images, pdf…'
    assert mediacenter.category.name == 'discover'
    assert mediacenter.template == 'ideascube/includes/cards/builtin.html'
    assert mediacenter.url == 'mediacenter:index'
    assert mediacenter.css_class == 'mediacenter'


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
