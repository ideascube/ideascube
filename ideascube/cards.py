import enum

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ideascube.configuration import get_config

# For unittesting purpose, we need to mock the Catalog class.
# However, the mock is made in a fixture and at this moment, we don't
# know where the mocked catalog will be used.
# So the fixture mocks 'ideascube.serveradmin.catalog.Catalog'.
# If we want to use the mocked Catalog here, we must not import the
# Catalog class directly but reference it from ideascube.serveradmin.catalog
# module.
from ideascube.serveradmin import catalog as catalog_mod


class Category(enum.Enum):
    create = _('create')
    discover = _('discover')
    manage = _('manage')
    read = _('read')


class Card:
    id = None
    name = None
    description = None
    category = None
    picto = None
    is_staff = False
    template = 'ideascube/includes/cards/builtin.html'

    @property
    def css_class(self):
        return self.id

    @property
    def url(self):
        return '%s:index' % self.id


class BlogCard(Card):
    id = 'blog'
    name = _('Blog')
    description = _('Browse blog posts.')
    category = Category.create


class LibraryCard(Card):
    id = 'library'
    name = _('Library')
    description = _('Browse books.')
    category = Category.read


class MediaCenterCard(Card):
    id = 'mediacenter'
    name = _('Medias center')
    description = _('Browse videos, sounds, images, pdf…')
    category = Category.discover


class StaffCard(Card):
    is_staff = True
    css_class = ''
    category = Category.manage


class EntriesCard(StaffCard):
    id = 'entry'
    name = _('Entries')
    description = _('Manage user entries.')
    picto = 'sign-in'
    url = 'monitoring:entry'


class LoansCard(StaffCard):
    id = 'loan'
    name = _('Loans')
    description = _('Manage loans.')
    picto = 'exchange'
    url = 'monitoring:loan'


class StockCard(StaffCard):
    id = 'stock'
    name = _('Stock')
    description = _('Manage stock.')
    picto = 'barcode'
    url = 'monitoring:stock'


class UsersCard(StaffCard):
    id = 'user'
    name = _('Users')
    description = _('Create, remove or modify users.')
    picto = 'users'
    url = 'user_list'


class SettingsCard(StaffCard):
    id = 'settings'
    name = _('Settings')
    description = _('Configure the server')
    picto = 'cog'
    url = 'server:settings'


BUILTIN_APP_CARDS = {
    'blog': BlogCard(),
    'library': LibraryCard(),
    'mediacenter': MediaCenterCard(),
}
STAFF_CARDS = {
    'entry': EntriesCard(),
    'loan': LoansCard(),
    'stock': StockCard(),
    'user': UsersCard(),
    'settings': SettingsCard(),
}


def build_builtin_card_info():
    card_ids = settings.BUILTIN_APP_CARDS
    return [BUILTIN_APP_CARDS[i] for i in card_ids]


def build_staff_card_info():
    card_ids = settings.STAFF_HOME_CARDS
    return [STAFF_CARDS[i] for i in card_ids]


def build_extra_app_card_info():
    card_ids = settings.EXTRA_APP_CARDS
    return [{'id': i} for i in card_ids]


def build_package_card_info():
    package_card_info = []
    catalog = catalog_mod.Catalog()
    packages_to_display = catalog.list_installed(get_config('home-page', 'displayed-package-ids'))

    for package in packages_to_display:
        card_info = {
            'id': package.template_id,
            'name': package.name,
            'description': getattr(package, 'description', ''),
            'lang': getattr(package, 'language', ''),
            'package_id': package.id,
            'is_staff': getattr(package, 'staff_only', False),
            'theme': getattr(package, 'theme', None),
            'css_class': getattr(package, 'css_class', None)
        }
        package_card_info.append(card_info)
    return package_card_info
