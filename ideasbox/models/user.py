from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):

    def create_user(self, serial, password=None):
        if not serial:
            raise ValueError('Users must have a serial')

        user = self.model(
            serial=serial
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, serial, password):
        user = self.create_user(serial=serial, password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class AbstractUser(AbstractBaseUser):
    USERNAME_FIELD = 'serial'

    LANG_KNOWLEDGE_CHOICES = (
        (1, 'Understood'),
        (2, 'Written'),
        (3, 'Spoken'),
        (4, 'Read'),
    )

    serial = models.CharField(max_length=40, unique=True)
    short_name = models.CharField(_('usual name'), max_length=30, blank=True)
    full_name = models.CharField(_('full name'), max_length=100, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user '
                                               'can log into this admin '
                                               'site.'))

    objects = UserManager()

    class Meta:
        abstract = True

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.short_name


class DefaultUser(AbstractUser):
    pass


class ProfileMixin(object):

    # Should we use numeric indexes? Maybe using string make the data in the db
    # more robust for backup/restore between different code versions.
    BOX_AWARENESS_CHOICES = (
        (1, _('Seen the Box')),
        (2, _('Has been informed by partner organization')),
        (3, _('Word of mouth')),
        (4, _('Poster campaign')),
        (5, _('Other')),
    )

    SCHOOL_LEVEL_CHOICES = (
        (1, _('Primary')),
        (2, _('Secondary')),
        (3, _('Professional')),
        (4, _('College')),
    )

    MARITAL_STATUS_CHOICES = (
        (1, _('Couple')),
        (2, _('Single')),
        (3, _('Widowed')),
    )

    # Do we want a fixed choice list instead of a text field?
    nationaliy = models.CharField(_('Nationality'), max_length=100, blank=True)
    city = models.CharField(_('City of origin'), max_length=100, blank=True)
    id_card_number = models.CharField(_('ID card number'), max_length=50,
                                      blank=True)
    children_under_12 = models.PositiveSmallIntegerField(
        _('Number of children under 12'),
        blank=True)
    children_under_18 = models.PositiveSmallIntegerField(
        _('Number of children under 18'),
        blank=True)
    children_above_18 = models.PositiveSmallIntegerField(
        _('Number of children above 18'),
        blank=True)
    school_level = models.PositiveSmallIntegerField(
        _('School level'),
        choices=SCHOOL_LEVEL_CHOICES,
        blank=True)
    marital_status = models.PositiveSmallIntegerField(
        _('Family status'),
        choices=MARITAL_STATUS_CHOICES,
        blank=True)
    box_awareness = models.PositiveSmallIntegerField(
        _('Ideas Box awareness'),
        choices=BOX_AWARENESS_CHOICES,
        blank=True)


class RefugeeMixin(object):

    OCCUPATION_CHOICES = (
        (1, _('Student')),
        (2, _('Teacher')),
        (3, _('Without profession')),
        (4, _('Profit profession')),
        (5, _('Other')),
    )

    FAMILY_STATUS_CHOICES = (
        (1, _('Lives with family in the camp')),
        (2, _('Lives without family in the camp')),
        (3, _('Has family in the camp but lives without')),
    )

    CAMP_ACTIVITY_CHOICES = (
        (1, 'Comitees, representation groups'),
        (2, 'Music, dance, singing'),
        (3, 'Other cultural activities'),
        (4, 'Informatic workshops'),
        (5, 'Literacy working group'),
        (6, 'Talking group'),
        (7, 'Children activities'),
        (8, 'Other'),
    )

    refugee_id = models.CharField(_('Refugee ID'), max_length=100, blank=True)
    camp_entry_date = models.DateField(_('Camp entry date'))
    current_occupation = models.PositiveSmallIntegerField(
        _('Current occupation'),
        choices=OCCUPATION_CHOICES,
        blank=True)
    country_of_origin_occupation = models.CharField(
        _('Occupation in the country of origin'),
        max_length=100,
        blank=True)
    family_status = models.PositiveSmallIntegerField(
        _('Family status'),
        choices=FAMILY_STATUS_CHOICES,
        blank=True)
    is_sent_to_school = models.BooleanField(_('Sent to school (if under 18)'))
    camp_activities = models.CommaSeparatedIntegerField(
        choices=CAMP_ACTIVITY_CHOICES)


class SwahiliLangMixin(object):
    sw_level = models.PositiveSmallIntegerField(
        _('Swahili knowledge'),
        choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True)


class FrenchLangMixin(object):
    fr_level = models.PositiveSmallIntegerField(
        _('French knowledge'),
        choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True)


class KirundiLangMixin(object):
    rn_level = models.PositiveSmallIntegerField(
        _('Kirundi knowledge'),
        choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True)


class BurundiRefugeeUser(AbstractUser, ProfileMixin, RefugeeMixin,
                         SwahiliLangMixin, FrenchLangMixin, KirundiLangMixin):
    """
    User for UNHCR Boxes, in Burundi.
    """
    pass


class BurundiMakambaUser(AbstractUser, ProfileMixin, SwahiliLangMixin,
                         FrenchLangMixin, KirundiLangMixin):
    """
    User for Makamba Box, run by the PNUD, and not in a refugees camp.
    """
    pass
