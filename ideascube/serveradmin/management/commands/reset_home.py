from django.core.management.base import BaseCommand

from ideascube.models import User
from ideascube.configuration import set_config
from ideascube.serveradmin import catalog


class Command(BaseCommand):
    help = 'Reset the displayed home cards to all installed packages'

    def handle(self, *_, **options):
        pkgs = catalog.Catalog().list_installed(['*'])
        pkg_ids = [pkg.id for pkg in pkgs]
        user = User.objects.get_system_user()
        set_config('home-page', 'displayed-package-ids', pkg_ids, user)
