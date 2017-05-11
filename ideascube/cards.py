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
    """The representation of a card on the Ideascube home page

    This class, and its subclasses, are expected to have the following
    attributes:

    * id: the unique identifier of the card;
    * name: the user-visible name of the card;
    * description: the user-visible description of the card;
    * category: the category of the card, which is guaranteed to be a member of
        the Category enumeration;
    * picto: the name of a Font Awesome glyph, without the "fa-" prefix;
    * is_staff: whether or not the card is only visible to the staff;
    * template: the path to the Django template used to render the card;
    * url: the URL of the page pointed to by a click on the card;
    * css_class: the CSS class given to the class DOM element;

    Those attributes will always be readable on all instances of this class and
    its subclasses, and are read when building the home page.
    """
    id = None
    name = None
    description = None
    category = None
    picto = None
    is_staff = False
    template = 'ideascube/includes/cards/builtin.html'
    url = None
    css_class = None


class BuiltinCard(Card):
    def __init__(self, id, name, description, category):
        self.id = id
        self.name = name
        self.description = description
        self.category = category

    @property
    def url(self):
        return '%s:index' % self.id

    @property
    def css_class(self):
        return self.id


class StaffCard(Card):
    is_staff = True
    css_class = ''
    category = Category.manage

    def __init__(self, id, name, description, picto, url):
        self.id = id
        self.name = name
        self.description = description
        self.picto = picto
        self.url = url


BUILTIN_APP_CARDS = {
    'blog': BuiltinCard(
        'blog', _('Blog'), _('Browse blog posts.'), Category.create),
    'library': BuiltinCard(
        'library', _('Library'), _('Browse books.'), Category.read),
    'mediacenter': BuiltinCard(
        'mediacenter', _('Medias center'),
        _('Browse videos, sounds, images, pdf…'), Category.discover),
}
STAFF_CARDS = {
    'entry': StaffCard(
        'entry', _('Entries'), _('Manage user entries.'), 'sign-in',
        'monitoring:entry'),
    'loan': StaffCard(
        'loan', _('Loans'), _('Manage loans.'), 'exchange', 'monitoring:loan'),
    'stock': StaffCard(
        'stock', _('Stock'), _('Manage stock.'), 'barcode',
        'monitoring:stock'),
    'users': StaffCard(
        'users', _('Users'), _('Create, remove or modify users.'), 'users',
        'user_list'),
    'settings': StaffCard(
        'settings', _('Settings'), _('Configure the server.'), 'cog',
        'server:settings'),
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
