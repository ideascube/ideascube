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
    assert library.picto is None
    assert library.is_staff is False
    assert library.template == 'ideascube/includes/cards/builtin.html'
    assert library.url == 'library:index'
    assert library.css_class == 'library'

    mediacenter = cards[1]
    assert mediacenter.id == 'mediacenter'
    assert mediacenter.name == 'Medias center'
    assert mediacenter.description == 'Browse videos, sounds, images, pdf…'
    assert mediacenter.category.name == 'discover'
    assert mediacenter.picto is None
    assert mediacenter.is_staff is False
    assert mediacenter.template == 'ideascube/includes/cards/builtin.html'
    assert mediacenter.url == 'mediacenter:index'
    assert mediacenter.css_class == 'mediacenter'


def test_build_staff_card_info(settings):
    from ideascube.cards import build_staff_card_info

    settings.STAFF_HOME_CARDS = ['settings', 'users', 'stock']

    cards = build_staff_card_info()
    assert len(cards) == 3

    settings = cards[0]
    assert settings.id == 'settings'
    assert settings.name == 'Settings'
    assert settings.description == 'Configure the server.'
    assert settings.category.name == 'manage'
    assert settings.picto == 'cog'
    assert settings.is_staff is True
    assert settings.template == 'ideascube/includes/cards/builtin.html'
    assert settings.url == 'server:settings'
    assert settings.css_class == ''

    users = cards[1]
    assert users.id == 'users'
    assert users.name == 'Users'
    assert users.description == 'Create, remove or modify users.'
    assert users.category.name == 'manage'
    assert users.picto == 'users'
    assert users.is_staff is True
    assert users.template == 'ideascube/includes/cards/builtin.html'
    assert users.url == 'user_list'
    assert users.css_class == ''

    stock = cards[2]
    assert stock.id == 'stock'
    assert stock.name == 'Stock'
    assert stock.description == 'Manage stock.'
    assert stock.category.name == 'manage'
    assert stock.picto == 'barcode'
    assert stock.is_staff is True
    assert stock.template == 'ideascube/includes/cards/builtin.html'
    assert stock.url == 'monitoring:stock'
    assert stock.css_class == ''


def test_build_extra_app_card_info(settings):
    from ideascube.cards import build_extra_app_card_info

    settings.EXTRA_APP_CARDS = ['bsfcampus', 'appinventor']

    cards = build_extra_app_card_info()
    assert len(cards) == 2

    bsfcampus = cards[0]
    assert bsfcampus.id == 'bsfcampus'
    assert bsfcampus.name == 'BSF Campus'
    assert bsfcampus.description == (
        'Renforcer les capacités des bibliothèques.')
    assert bsfcampus.category.name == 'learn'
    assert bsfcampus.picto is None
    assert bsfcampus.is_staff is False
    assert bsfcampus.template == 'ideascube/includes/cards/external.html'
    assert bsfcampus.url == 'http://bsfcampus.ideascube.lan/'
    assert bsfcampus.css_class == 'bsfcampus'

    appinventor = cards[1]
    assert appinventor.id == 'appinventor'
    assert appinventor.name == 'App Inventor'
    assert appinventor.description == (
        'Create your own apps for Android.')
    assert appinventor.category.name == 'create'
    assert appinventor.picto is None
    assert appinventor.is_staff is False
    assert appinventor.template == 'ideascube/includes/cards/external.html'
    assert appinventor.url == 'http://appinventor.ideascube.lan/'
    assert appinventor.css_class == 'appinventor'


def test_build_package_card_info_must_not_fail_for_no_package(systemuser):
    from ideascube.configuration import set_config
    from ideascube.cards import build_package_card_info
    set_config('home-page', 'displayed-package-ids', ['test.package1'], systemuser)
    assert build_package_card_info() == []


def test_build_package_card_info(systemuser, catalog):
    from ideascube.configuration import set_config
    from ideascube.cards import build_package_card_info
    from ideascube.serveradmin.catalog import (
        StaticSite, ZippedZim, ZippedMedias)

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
    catalog.add_mocked_package(StaticSite('test.package3.fr', {
        'name': 'Test package3',
        'description': 'Test package3 description',
        'language': 'fr',
        'staff_only': False}))
    set_config('home-page', 'displayed-package-ids', ['test.package1.fr', 'test.package2.fr', 'test.package3.fr'], systemuser)

    cards = build_package_card_info()
    assert len(cards) == 3

    pkg1 = cards[0]
    assert pkg1.id == 'test.package1.fr'
    assert pkg1.name == 'Test package1'
    assert pkg1.description == 'Test package1 description'
    assert pkg1.category.name == 'learn'
    assert pkg1.picto is None
    assert pkg1.is_staff is False
    assert pkg1.template == 'ideascube/includes/cards/external.html'
    assert pkg1.url == 'http://kiwix.ideascube.lan/test.package1.fr/'
    assert pkg1.css_class == 'test.package1'

    pkg2 = cards[1]
    assert pkg2.id == 'test.package2.fr'
    assert pkg2.name == 'Test package2'
    assert pkg2.description == 'Test package2 description'
    assert pkg2.category.name == 'discover'
    assert pkg2.picto is None
    assert pkg2.is_staff is False
    assert pkg2.template == 'ideascube/includes/cards/media-package.html'
    assert pkg2.url is None
    assert pkg2.css_class == 'mediacenter'

    pkg3 = cards[2]
    assert pkg3.id == 'test.package3.fr'
    assert pkg3.name == 'Test package3'
    assert pkg3.description == 'Test package3 description'
    assert pkg3.category.name == 'info'
    assert pkg3.picto is None
    assert pkg3.is_staff is False
    assert pkg3.template == 'ideascube/includes/cards/external.html'
    assert pkg3.url == 'http://sites.ideascube.lan/test.package3.fr/'
    assert pkg3.css_class == 'test'
