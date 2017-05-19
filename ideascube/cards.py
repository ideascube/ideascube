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


class ExtraAppCard(Card):
    template = 'ideascube/includes/cards/external.html'

    @property
    def url(self):
        return 'http://%s.%s/' % (self.id, settings.DOMAIN)


class AppInventorCard(ExtraAppCard):
    id = 'appinventor'
    name = 'App Inventor'
    description = _('Create your own apps for Android.')
    category = Category.create


class BSFCampusCard(ExtraAppCard):
    id = 'bsfcampus'
    name = 'BSF Campus'
    description = (  # This is only for French-speaking people at the moment
        'Renforcer les capacités des bibliothèques.')
    category = Category.learn


class KhanAcademyCard(ExtraAppCard):
    id = 'khanacademy'
    name = 'Khan Academy'
    description = _('Learn with videos and exercises.')
    category = Category.learn


class KoomBookEduCard(ExtraAppCard):
    id = 'koombookedu'
    name = 'KoomBook EDU'
    description = (  # This is only for French-speaking people at the moment
        "Plateforme d'e-learning ouverte aux <br /> "
        "étudiants et aux professeurs.")
    category = Category.learn


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

    @property
    def category(self):
        name = getattr(self._package, 'theme', '')
        return getattr(Category, name, '')

    @property
    def css_class(self):
        return getattr(self._package, 'css_class', '')


class PackagedMediasCard(PackageCard):
    category = Category.discover
    css_class = 'mediacenter'
    template = 'ideascube/includes/cards/media-package.html'


class PackagedStaticSiteCard(PackageCard):
    template = 'ideascube/includes/cards/external.html'

    @property
    def url(self):
        return 'http://sites.%s/%s/' % (settings.DOMAIN, self.id)


class PackagedZimCard(PackageCard):
    template = 'ideascube/includes/cards/external.html'

    @property
    def url(self):
        return 'http://kiwix.%s/%s/' % (settings.DOMAIN, self.id)


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
EXTRA_APP_CARDS = {
    'appinventor': AppInventorCard(),
    'bsfcampus': BSFCampusCard(),
    'khanacademy': KhanAcademyCard(),
    'koombookedu': KoomBookEduCard(),
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
