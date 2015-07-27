import re
from datetime import date

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from .models import Entry, InventorySpecimen, Loan, Specimen

user_model = get_user_model()


class EntryForm(forms.Form):

    serials = forms.CharField(widget=forms.Textarea(attrs={
            'placeholder': _('Enter user serials'),
            'rows': 4
        }))
    module = forms.CharField(widget=forms.HiddenInput, required=False)
    activity = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'placeholder': _('Enter a activity name if missing on the list')}))
    partner = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'placeholder': _('Partner involved in activity')}))
    activity_list = forms.ChoiceField(
        choices=[('', '------')] + settings.ENTRY_ACTIVITY_CHOICES,
        required=False)

    def clean_module(self):
        for key, label in Entry.MODULES:
            if 'entry_{0}'.format(key) in self.data:
                return key
        raise forms.ValidationError(_('Missing module name'))

    def clean_serials(self):
        serials = self.cleaned_data['serials']
        return set([s for s in serials.splitlines() if s])


class ExportEntryForm(forms.Form):

    since = forms.DateField(
        widget=forms.DateInput(format='%Y-%m-%d'),
        required=False)


class SpecimenForm(forms.ModelForm):

    def clean_barcode(self):
        # Keep only integers and letters, and make sure empty values are mapped
        # to None, not empty string (we need NULL values in db, not empty
        # strings, for uniqueness constraints).
        return re.sub(r'\W', '', self.cleaned_data['barcode']) or None

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


class LoanForm(forms.ModelForm):
    specimen = forms.CharField(widget=forms.TextInput(attrs={
                               'placeholder': _('Enter an item barcode')}))
    user = forms.CharField(widget=forms.TextInput(attrs={
                               'placeholder': _('Enter a user serial')}))
    due_date = forms.DateField(widget=forms.DateInput(format='%Y-%m-%d'),
                               initial=date.today)

    def clean_specimen(self):
        barcode = self.cleaned_data['specimen']
        if Loan.objects.filter(specimen__barcode=barcode).exists():
            msg = _('Item with barcode {barcode} is already loaned.')
            forms.ValidationError(msg.format(barcode=barcode))
        try:
            specimen = Specimen.objects.get(barcode=barcode)
        except Specimen.DoesNotExist:
            raise forms.ValidationError(
                _('Bar code {barcode} not found'.format(barcode=barcode)))
        else:
            return specimen

    def clean_user(self):
        serial = self.cleaned_data['user']
        try:
            user = user_model.objects.get(serial=serial)
        except user_model.DoesNotExist:
            raise forms.ValidationError(
                _('Serial {serial} not found'.format(serial=serial)))
        else:
            return user

    class Meta:
        model = Loan
        exclude = ['by']


class ReturnForm(forms.Form):
    loan = forms.CharField(widget=forms.TextInput(attrs={
                           'placeholder': _('Enter an item barcode')}))

    def clean_loan(self):
        barcode = self.cleaned_data['loan']
        try:
            loan = Loan.objects.get(specimen__barcode=barcode)
        except Loan.DoesNotExist:
            msg = _('Item with barcode {barcode} is not loaned.')
            forms.ValidationError(msg.format(barcode=barcode))
        else:
            return loan
