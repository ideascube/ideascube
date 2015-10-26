# Configuration

## Python configuration

The first way of customizing the project installation is to provide a local
settings file.
This can be done in three ways:

- add a file `hostname`.py in `ideascube/conf` (for example, `ideabox/conf/azraq.py`
  if the `hostname` is `azraq`)
- set an environment variable `IDEASCUBE_ID` and add a file with this id in `ideascube/conf`
- define `DJANGO_SETTINGS_MODULE` environment variable

Good reading:
- Django documentation about [settings](https://docs.djangoproject.com/en/1.8/ref/settings/)
- examples of local [settings](https://github.com/ideas-box/ideascube/tree/master/ideascube/conf)

### Main settings

Among all Django and custom settings, here are the one you may want to customize.

#### IDEASCUBE_NAME = *string*

The displayed server name in the header.

#### TIME_ZONE = *string*

The timezone of the server. One of [this list](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

#### LANGUAGE_CODE = *iso code*

The default language of the server. One of this [identifiers list](http://www.i18nguy.com/unicode/language-identifiers.html).

#### COUNTRIES_FIRST = *list of iso codes*

The countries to appear first in the user form select.

```python
COUNTRIES_FIRST = ['SY', 'JO']
```

#### MONITORING_ENTRY_EXPORT_FIELDS = *list of field names*

List of user fields to be exposed when exporting "entries".

```python
MONITORING_ENTRY_EXPORT_FIELDS = ['serial', 'refugee_id', 'birth_year', 'gender']
```

#### USER_FORM_FIELDS = *list of tuples*

The fields we want on the user object. Each tuple is (category name, list of fields).

```python
USER_FORM_FIELDS = (
    ('Ideasbox', ['serial', 'box_awareness']),
    (_('Personal informations'), ['refugee_id', 'short_name', 'full_name', 'latin_name', 'birth_year', 'gender']),  # noqa
    (_('Family'), ['marital_status', 'family_status', 'children_under_12', 'children_under_18', 'children_above_18']),  # noqa
    (_('In the camp'), ['camp_entry_date', 'camp_activities', 'current_occupation', 'camp_address']),  # noqa
    (_('Origin'), ['country', 'city', 'country_of_origin_occupation', 'school_level', 'is_sent_to_school']),  # noqa
    (_('Language skills'), ['ar_level', 'en_level']),
    (_('National residents'), ['id_card_number']),
)
```
