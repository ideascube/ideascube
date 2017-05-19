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
    info = _('info')
    learn = _('learn')
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


class ExtraAppCard(BuiltinCard):
    template = 'ideascube/includes/cards/external.html'

    @property
    def url(self):
        return 'http://%s.%s/' % (self.id, settings.DOMAIN)


class PackageCard(Card):
    def __init__(self, package):
        self._package = package

    @property
    def id(self):
        return self._package.id

    @property
    def name(self):
        return self._package.name

    @property
    def description(self):
        return getattr(self._package, 'description', '')


class PackagedMediasCard(PackageCard):
    category = Category.discover
    css_class = 'mediacenter'
    template = 'ideascube/includes/cards/media-package.html'


class PackagedStaticSiteCard(PackageCard):
    template = 'ideascube/includes/cards/external.html'

    # FIXME: This is a fragile hack, and should be a package metadata
    @property
    def category(self):
        if '.map' in self.id or self.id in ['maguare.es', 'cinescuela.es']:
            return Category.discover

        return Category.info

    @property
    def url(self):
        return 'http://sites.%s/%s/' % (settings.DOMAIN, self.id)

    # FIXME: This is a fragile hack, and should be a package metadata
    @property
    def css_class(self):
        if '.map' in self.id:
            return 'maps'

        base_name, *_ = self.id.split('.')
        return base_name


class PackagedZimCard(PackageCard):
    template = 'ideascube/includes/cards/external.html'

    # FIXME: This is a fragile hack, and should be a package metadata
    @property
    def category(self):
        base_name, _ = self.id.rsplit('.', 1)

        if base_name in ("wikipedia", "wikivoyage", "vikidia"):
            return Category.discover

        if base_name in ("gutemberg", "icd10", "wikisource", "wikibooks", "bouquineux"):
            return Category.read

        return Category.learn

    @property
    def url(self):
        return 'http://kiwix.%s/%s/' % (settings.DOMAIN, self.id)

    # FIXME: This is a fragile hack, and should be a package metadata
    @property
    def css_class(self):
        base_name, _ = self.id.rsplit('.', 1)

        if base_name.startswith('ted'):
            return 'ted'

        return base_name


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
EXTRA_APP_CARDS = {
    'appinventor': ExtraAppCard(
        'appinventor', 'App Inventor', _('Create your own apps for Android.'),
        Category.create),
    'bsfcampus': ExtraAppCard(
        'bsfcampus', 'BSF Campus',
        # This is only for French-speaking people at the moment
        'Renforcer les capacités des bibliothèques.',
        Category.learn
        ),
    'khanacademy': ExtraAppCard(
        'khanacademy', 'Khan Academy', _('Learn with videos and exercises.'),
        Category.learn),
    'koombookedu': ExtraAppCard(
        'koombookedu', 'KoomBook EDU',
        # This is only for French-speaking people at the moment
        "Plateforme d'e-learning ouverte aux<br />étudiants et aux "
        "professeurs.", Category.learn),
}
PACKAGED_CARDS = {
    'static-site': PackagedStaticSiteCard,
    'zipped-medias': PackagedMediasCard,
    'zipped-zim': PackagedZimCard,
}


def build_builtin_card_info():
    card_ids = settings.BUILTIN_APP_CARDS
    return [BUILTIN_APP_CARDS[i] for i in card_ids]


def build_staff_card_info():
    card_ids = settings.STAFF_HOME_CARDS
    return [STAFF_CARDS[i] for i in card_ids]


def build_extra_app_card_info():
    # FIXME: Eventually this needs to know whether the extra app is installed,
    #        and get the metadata from there, like the packaged apps.
    #        https://framagit.org/ideascube/ideascube/issues/810
    card_ids = settings.EXTRA_APP_CARDS
    return [EXTRA_APP_CARDS[i] for i in card_ids]


def build_package_card_info():
    catalog = catalog_mod.Catalog()
    packages_to_display = catalog.list_installed(get_config('home-page', 'displayed-package-ids'))

    return [
        PACKAGED_CARDS[package.typename](package)
        for package in packages_to_display
    ]


def build_custom_card_info():
    cards = settings.CUSTOM_CARDS

    for card in cards:
        card['category'] = getattr(Category, card['category'])
        card['template'] = 'ideascube/includes/cards/external.html'

    return cards
