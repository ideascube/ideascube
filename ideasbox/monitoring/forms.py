import re

from django import forms
from django.utils.translation import ugettext as _

from .models import Entry, InventorySpecimen, Specimen


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


class SpecimenForm(forms.ModelForm):

    def clean_barcode(self):
        # Keep only integers, and make sure empty values are mapped to None,
        # not empty string (we need NULL values in db, not empty strings, for
        # uniqueness constraints).
        return re.sub(r'\D', '', self.cleaned_data['barcode']) or None

    class Meta:
        model = Specimen
        widgets = {'item': forms.HiddenInput}
        fields = '__all__'


class InventorySpecimenForm(forms.ModelForm):

    specimen = forms.CharField(widget=forms.TextInput(attrs={
                               'placeholder': _('Enter a bar code')}))

    def clean_specimen(self):
        barcode = self.cleaned_data['specimen']
        try:
            specimen = Specimen.objects.get(barcode=barcode)
        except Specimen.DoesNotExist:
            raise forms.ValidationError(
                _('Bar code {barcode} not found'.format(barcode=barcode)))
        else:
            return specimen

    class Meta:
        model = InventorySpecimen
        widgets = {'inventory': forms.HiddenInput, 'count': forms.HiddenInput}
        fields = '__all__'
