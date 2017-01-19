import csv
import re
from datetime import date

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from ideascube.utils import TextIOWrapper

from .models import Entry, InventorySpecimen, Loan, Specimen, StockItem

user_model = get_user_model()


def clean_barcode(barcode):
    # Keep only integers and letters, and make sure empty values are mapped
    # to None, not empty string (we need NULL values in db, not empty
    # strings, for uniqueness constraints).
    return re.sub(r'\W', '', barcode) or None


class EntryForm(forms.Form):

    serials = forms.CharField(widget=forms.Textarea(attrs={
            'placeholder': _('Enter user identifiers'),
            'rows': 4
        }))
    module = forms.CharField(widget=forms.HiddenInput, required=False)
    activity = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'placeholder': _('Custom activity name')}))
    partner = forms.CharField(required=False, widget=forms.TextInput(attrs={
            'placeholder': _('Partner involved in activity')}))

    if settings.ENTRY_ACTIVITY_CHOICES:
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


class SinceForm(forms.Form):

    since = forms.DateField(label=_('since'),
                            widget=forms.DateInput(format='%Y-%m-%d'),
                            required=False)


class ExportEntryForm(SinceForm):
    pass


class ExportLoanForm(SinceForm):
    pass


class SpecimenForm(forms.ModelForm):

    def clean_barcode(self):
        return clean_barcode(self.cleaned_data['barcode'])

    class Meta:
        model = Specimen
        widgets = {'item': forms.HiddenInput}
        fields = '__all__'


class InventorySpecimenForm(forms.ModelForm):

    specimen = forms.CharField(label=_('specimen'),
                               widget=forms.TextInput(attrs={
                                   'placeholder': _('Enter a barcode')}))

    def clean_specimen(self):
        barcode = clean_barcode(self.cleaned_data['specimen'])
        try:
            specimen = Specimen.objects.get(barcode=barcode)
        except Specimen.DoesNotExist:
            raise forms.ValidationError(
                _('Barcode {barcode} not found').format(barcode=barcode))
        else:
            return specimen

    class Meta:
        model = InventorySpecimen
        widgets = {'inventory': forms.HiddenInput, 'count': forms.HiddenInput}
        fields = '__all__'


class LoanForm(forms.ModelForm):
    specimen = forms.CharField(label=_('specimen'),
                               widget=forms.TextInput(attrs={
                                   'placeholder': _('Enter an item barcode')}))
    user = forms.CharField(label=_('user'),
                           widget=forms.TextInput(attrs={
                               'placeholder': _('Enter a user identifier')}))
    due_date = forms.DateField(label=_('due date'),
                               widget=forms.DateInput(format='%Y-%m-%d'),
                               initial=date.today)

    def clean_specimen(self):
        barcode = self.cleaned_data['specimen']
        if Loan.objects.due().filter(specimen__barcode=barcode).exists():
            msg = _('Item with barcode {barcode} is already loaned.')
            raise forms.ValidationError(msg.format(barcode=barcode))
        try:
            specimen = Specimen.objects.get(barcode=barcode)
        except Specimen.DoesNotExist:
            raise forms.ValidationError(
                _('Barcode {barcode} not found').format(barcode=barcode))
        else:
            return specimen

    def clean_user(self):
        serial = self.cleaned_data['user']
        try:
            user = user_model.objects.get(serial=serial)
        except user_model.DoesNotExist:
            raise forms.ValidationError(
                _('Identifier {serial} not found').format(serial=serial))
        else:
            return user

    class Meta:
        model = Loan
        exclude = ['by', 'returned_at']


class ReturnForm(forms.Form):
    loan = forms.CharField(label=_('specimen'),
                           widget=forms.TextInput(attrs={
                               'placeholder': _('Enter an item barcode')}))

    def clean_loan(self):
        barcode = self.cleaned_data['loan']
        try:
            loan = Loan.objects.due().get(specimen__barcode=barcode)
        except Loan.DoesNotExist:
            msg = _('Item with barcode {barcode} is not loaned.')
            raise forms.ValidationError(msg.format(barcode=barcode))
        except Loan.MultipleObjectsReturned:
            # Should araise only after migration 0.3.2 to 0.3.0.
            loan = Loan.objects.due().filter(specimen__barcode=barcode).first()
        return loan


class StockItemForm(forms.ModelForm):
    class Meta:
        fields = ['module', 'name', 'description']
        model = StockItem


class StockImportForm(forms.Form):
    source = forms.FileField(label=_('CSV File'), required=True)

    def save(self):
        source = TextIOWrapper(self.cleaned_data['source'].file)
        items = []
        errors = []

        for index, row in enumerate(csv.DictReader(source)):
            try:
                data = {
                    'module': row['module'], 'name': row['name'],
                    'description': row['description'],
                }

            except KeyError as e:
                errors.append(_('Missing column "{}" on line {}').format(
                    e.args[0], index + 1))
                continue

            form = StockItemForm(data=data)

            if form.is_valid():
                item = form.save()
                items.append(item)

            else:
                msgs = (
                    '{}: {}'.format(k, v.as_text())
                    for k, v in form.errors.items())
                errors.append(_('Could not import line {}: {}').format(
                    index + 1, '; '.join(msgs)))
                continue

        return items, errors[:10]
