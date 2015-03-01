from django import forms
from django.utils.translation import ugettext as _

from .models import Entry


class EntryForm(forms.Form):

    serials = forms.CharField(widget=forms.Textarea(attrs={
            'placeholder': _('Enter user serials'),
            'rows': 4
        }))
    module = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_module(self):
        for key, label in Entry.MODULES:
            if 'entry_{0}'.format(key) in self.data:
                return key
        raise forms.ValidationError(_('Missing module name'))

    def clean_serials(self):
        serials = self.cleaned_data['serials']
        return [s for s in serials.splitlines() if s]


class ExportEntryForm(forms.Form):

    since = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d'),
        required=False)
