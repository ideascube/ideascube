from ideascube.configuration import get_config

# For unittesting purpose, we need to mock the Catalog class.
# However, the mock is made in a fixture and at this moment, we don't
# know where the mocked catalog will be used.
# So the fixture mocks 'ideascube.serveradmin.catalog.Catalog'.
# If we want to use the mocked Catalog here, we must not import the
# Catalog class directly but reference it from ideascube.serveradmin.catalog
# module.
from ideascube.serveradmin import catalog as catalog_mod


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
