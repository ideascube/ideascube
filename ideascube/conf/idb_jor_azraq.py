"""Azraq box in Jordan"""
from .idb import *  # pragma: no flakes
from django.utils.translation import ugettext_lazy as _

COUNTRIES_FIRST = ['SY', 'JO']
TIME_ZONE = 'Asia/Amman'
LANGUAGE_CODE = 'ar'
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'refugee_id', 'birth_year',
                                  'gender']
USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['refugee_id', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the camp'), ['camp_entry_date', 'camp_activities', 'current_occupation', 'camp_address']),  # noqa
    (_('Origin'), ['country', 'city', 'country_of_origin_occupation', 'school_level', 'is_sent_to_school']),  # noqa
    (_('Language skills'), ['ar_level', 'en_level']),
    (_('National residents'), ['id_card_number']),
)

ENTRY_ACTIVITY_CHOICES = [
    ('16 Days of Activism', _('16 Days of Activism')),
    ("AMANI Campaign", _("AMANI Campaign")),
    ("Anger Management Training", _("Anger Management Training")),
    ("Basic Computer Training", _("Basic Computer Training")),
    ("Beauty Training", _("Beauty Training")),
    ("Book Club", _("Book Club")),
    ("Conflict Resolution Training", _("Conflict Resolution Training")),
    ("Coping Skills and Mechanisms Training", _("Coping Skills and Mechanisms Training")),  # noqa
    ("EDRAAK", _("EDRAAK")),
    ("Emotional intelligence Training", _("Emotional intelligence Training")),
    ("Handicrafts", _("Handicrafts")),
    ("How to be a Psychosocial Counselor Training", _("How to be a Psychosocial Counselor Training")),  # noqa
    ("I am Woman", _("I am Woman")),
    ("International Children Day", _("International Children Day")),
    ("International Refugee Day", _("International Refugee Day")),
    ("Marathon", _("Marathon")),
    ("Mother's day celebration", _("Mother's day celebration")),
    ("Parenting Skills Training", _("Parenting Skills Training")),
    ("Peer Support Group", _("Peer Support Group")),
    ("Psychosocial ART Interventions Training", _("Psychosocial ART Interventions Training")),  # noqa
    ("Puppets and Theatre", _("Puppets and Theatre")),
    ("Sewing and stitching", _("Sewing and stitching")),
    ("SIMSIM Club", _("SIMSIM Club")),
    ("Social Work Training", _("Social Work Training")),
    ("Stress Management Training", _("Stress Management Training")),
    ("Training of Trainers", _("Training of Trainers")),
    ("World Mental Health Day", _("World Mental Health Day")),
]
