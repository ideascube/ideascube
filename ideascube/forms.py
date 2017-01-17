import csv

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .utils import TextIOWrapper
from .widgets import ComboBoxEntry


User = get_user_model()


class UserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                # Force date format on load, so date picker doesn't mess it up
                # because of i10n.
                field.widget = forms.DateInput(format='%Y-%m-%d')

            elif name == 'current_occupation':
                choices = self._get_choices(
                    'OCCUPATION_CHOICES', 'current_occupation')
                field.widget = ComboBoxEntry(choices=choices)

            if name == 'extra':
                field.label = getattr(
                    settings, 'USER_EXTRA_FIELD_LABEL', _('Additional data'))

    def _get_choices(self, attribute_defaults, attribute_used):
        default_choices = getattr(User, attribute_defaults)

        used_choices = User.objects.values_list(attribute_used, flat=True)
        used_choices = set(used_choices.distinct())

        # We can't simply get the union of default_choices and used_choices,
        # because elements of the former are (db_value, pretty_value) tuples,
        # while elements of the latter are a single value.
        #
        # Therefore we must first get only the used choices which are custom,
        # that is not part of the defaults.
        custom_choices = used_choices - {c[0] for c in default_choices}
        custom_choices = sorted(custom_choices)

        return tuple((c, c) for c in custom_choices) + default_choices

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_staff']


class CreateStaffForm(forms.ModelForm):
    serial = forms.CharField(label=_('Username'),
                             help_text="Spaces are not allowed")
    password = forms.CharField(label=_("Password"),
                               help_text=_('To create a strong password, '
                                           'forget about passwords, and think '
                                           'rather about a passphrase. For '
                                           'instance: "The boat is flowing on '
                                           'the water" is a strong and easy to'
                                           ' remember passphrase. Now choose '
                                           'your own passphrase!'),
                               widget=forms.PasswordInput)
    password_confirm = forms.CharField(label=_("Confirm password"),
                                       widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ['serial', 'password']

    def clean_password_confirm(self):
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirm')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('The two passwords do not match')
        return password2

    def save(self, *args, **kwargs):
        user = super().save(*args, **kwargs)
        password = self.cleaned_data['password']
        user.set_password(password)
        user.is_staff = True
        user.save()
        return user


class UserImportForm(forms.Form):
    source = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        formats = getattr(settings, 'USER_IMPORT_FORMATS', None)

        if formats is None:
            self.fields['format'] = forms.CharField(
                required=True, initial='ideascube', widget=forms.HiddenInput)

        else:
            self.fields['format'] = forms.ChoiceField(
                required=True, initial=formats[0][0], choices=formats)

    def _get_ideascube_reader(self, source):
        return csv.DictReader(source)

    def _get_ideascube_mapping(self, data):
        return data

    def _get_llavedelsaber_reader(self, source):
        return csv.DictReader(source, delimiter=';', quoting=csv.QUOTE_ALL)

    def _get_llavedelsaber_mapping(self, data):
        # TODO: Implement the rest, once we hear back from Sergio
        return {
            'serial': data['serial'],
        }

    def save(self):
        format = self.cleaned_data['format']
        source = TextIOWrapper(self.cleaned_data['source'].file)
        qs = User.objects.all()
        mapper = getattr(self, '_get_%s_mapping' % format)
        reader = getattr(self, '_get_%s_reader' % format)

        users = []
        errors = []

        for idx, row in enumerate(reader(source), start=1):
            try:
                row = mapper(row)

            except KeyError as e:
                msg = _('Invalid row at line {id}: {field} missing')
                errors.append(msg.format(id=idx, field=e.args[0]))
                continue

            try:
                instance = qs.get(serial=row['serial'])
            except (User.DoesNotExist, KeyError):
                instance = None
            form = UserForm(data=row, instance=instance)
            if form.is_valid():
                user = form.save()
                users.append(user)
            else:
                reason = ', '.join('{}: {}'.format(k, v.as_text())
                                   for k, v in form.errors.items())
                errors.append(_('Invalid row at line {id}: {reason}').format(
                    id=idx, reason=reason))
        return users, errors[:10]
