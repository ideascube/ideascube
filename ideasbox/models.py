from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField

from .fields import CommaSeparatedCharField
from .utils import classproperty


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    updating ``created_at`` and ``modified_at`` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-modified_at", ]


class UserManager(BaseUserManager):

    def create_user(self, serial, password=None, **extra):
        if not serial:
            raise ValueError('Users must have a serial')

        user = self.model(serial=serial, **extra)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, serial, password, **extra):
        user = self.create_user(serial=serial, password=password, **extra)
        user.is_staff = True
        user.save(using=self._db)
        return user


class AbstractUser(TimeStampedModel, AbstractBaseUser):
    """
    Minimum definition of a user. Inherit at least from this model.
    """
    USERNAME_FIELD = 'serial'

    LANG_KNOWLEDGE_CHOICES = (
        ('u', 'Understood'),
        ('w', 'Written'),
        ('s', 'Spoken'),
        ('r', 'Read'),
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

    def __unicode__(self):
        return self.get_full_name() or self.serial

    def get_absolute_url(self):
        return reverse('user_detail', kwargs={'pk': self.pk})

    def get_full_name(self):
        return self.full_name or self.get_short_name()

    def get_short_name(self):
        return self.short_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def public_fields(self):
        """Return user public fields labels and values."""
        exclude = ['last_login', 'password', 'id', 'is_staff']
        fields = [f for f in self._meta.fields if f.name not in exclude]

        def val(name):
            try:
                return getattr(self, 'get_{0}_display'.format(name))()
            except AttributeError:
                return getattr(self, name)

        return {f.name: {'label': f.verbose_name, 'value': val(f.name)}
                for f in fields}

    @classproperty
    @classmethod
    def REQUIRED_FIELDS(cls):
        """
        Make it dynamic, as we need to be able to run createsuperuser command
        with every user model.
        """
        already_included = ['serial', 'password']

        def wanted(field):
            return not any([field.blank, field.name in already_included,
                           field.has_default()])

        return [f.name for f in cls._meta.fields if wanted(f)]


class DefaultUser(AbstractUser):
    """
    Just a non abstrct version of the AbstractUser model. To be used mainly for
    dev and tests.
    """
    pass


class ProfileMixin(models.Model):

    # Should we use numeric indexes? Maybe using string make the data in the db
    # more robust for backup/restore between different code versions.
    BOX_AWARENESS_CHOICES = (
        ('seen_box', _('Seen the Box')),
        ('partner', _('Has been informed by partner organization')),
        ('word_of_mouth', _('Word of mouth')),
        ('campaign', _('Poster campaign')),
        ('other', _('Other')),
    )

    SCHOOL_LEVEL_CHOICES = (
        ('primary', _('Primary')),
        ('secondary', _('Secondary')),
        ('professional', _('Professional')),
        ('college', _('College')),
    )

    MARITAL_STATUS_CHOICES = (
        ('couple', _('Couple')),
        ('single', _('Single')),
        ('widowed', _('Widowed')),
    )

    GENDER_CHOICES = (
        ('undefined', _('Undefined')),
        ('male', _('Male')),
        ('female', _('Female')),
    )

    birth_year = models.PositiveSmallIntegerField(
        _('Birth year'), blank=True, null=True)
    gender = models.CharField(
        _('Gender'), choices=GENDER_CHOICES, blank=True,
        max_length=32)
    country = CountryField(_('Country of origin'), max_length=100, blank=True)
    city = models.CharField(_('City of origin'), max_length=100, blank=True)
    id_card_number = models.CharField(_('ID card number'), max_length=50,
                                      blank=True)
    children_under_12 = models.PositiveSmallIntegerField(
        _('Number of children under 12'),
        blank=True, null=True)
    children_under_18 = models.PositiveSmallIntegerField(
        _('Number of children under 18'),
        blank=True, null=True)
    children_above_18 = models.PositiveSmallIntegerField(
        _('Number of children above 18'),
        blank=True, null=True)
    school_level = models.CharField(
        _('School level'), choices=SCHOOL_LEVEL_CHOICES, blank=True,
        max_length=32)
    marital_status = models.CharField(
        _('Family status'), choices=MARITAL_STATUS_CHOICES, blank=True,
        max_length=32)
    box_awareness = models.CharField(
        _('Ideas Box awareness'), choices=BOX_AWARENESS_CHOICES, blank=True,
        max_length=32)

    class Meta:
        abstract = True


class RefugeeMixin(models.Model):

    OCCUPATION_CHOICES = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
        ('no_profession', _('Without profession')),
        ('profit_profession', _('Profit profession')),
        ('other', _('Other')),
    )

    FAMILY_STATUS_CHOICES = (
        ('with_family', _('Lives with family in the camp')),
        ('no_family', _('Lives without family in the camp')),
        ('without_family', _('Has family in the camp but lives without')),
    )

    CAMP_ACTIVITY_CHOICES = (
        ('comitees', 'Comitees, representation groups'),
        ('arts', 'Music, dance, singing'),
        ('other_arts', 'Other cultural activities'),
        ('informatic', 'Informatic workshops'),
        ('literacy', 'Literacy working group'),
        ('talking', 'Talking group'),
        ('children', 'Children activities'),
        ('other', 'Other'),
    )

    refugee_id = models.CharField(_('Refugee ID'), max_length=100, blank=True)
    camp_entry_date = models.DateField(_('Camp entry date'), blank=True,
                                       null=True)
    current_occupation = models.CharField(
        _('Current occupation'), choices=OCCUPATION_CHOICES, blank=True,
        max_length=32)
    country_of_origin_occupation = models.CharField(
        _('Occupation in the country of origin'),
        max_length=100,
        blank=True)
    family_status = models.CharField(
        _('Family status'), choices=FAMILY_STATUS_CHOICES, blank=True,
        max_length=32)
    is_sent_to_school = models.BooleanField(
        _('Sent to school (if under 18)'),
        default=False)
    camp_activities = models.CommaSeparatedIntegerField(
        _('Activities in the camp'),
        max_length=512,
        choices=CAMP_ACTIVITY_CHOICES,
        blank=True)

    class Meta:
        abstract = True


class SwahiliLangMixin(object):
    sw_level = CommaSeparatedCharField(
        _('Swahili knowledge'), choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True, max_length=32)

    class Meta:
        abstract = True


class FrenchLangMixin(object):
    fr_level = CommaSeparatedCharField(
        _('French knowledge'), choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True, max_length=32)

    class Meta:
        abstract = True


class KirundiLangMixin(models.Model):
    rn_level = CommaSeparatedCharField(
        _('Kirundi knowledge'), choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True, max_length=32)

    class Meta:
        abstract = True


class ArabicLangMixin(models.Model):
    ar_level = CommaSeparatedCharField(
        _('Arabic knowledge'), choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True, max_length=32)

    class Meta:
        abstract = True


class EnglishLangMixin(models.Model):
    en_level = CommaSeparatedCharField(
        _('English knowledge'), choices=AbstractUser.LANG_KNOWLEDGE_CHOICES,
        blank=True, max_length=32)

    class Meta:
        abstract = True


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


class AzraqUser(AbstractUser, ProfileMixin, RefugeeMixin, ArabicLangMixin,
                EnglishLangMixin):
    """
    User for Azraq camp box in Northen Jordan.
    """
    pass


class MaediUser(AbstractUser, ProfileMixin, ArabicLangMixin, EnglishLangMixin):
    """
    User for MAEDI box in Lebanon.
    """
    pass
