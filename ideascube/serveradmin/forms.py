from django.utils.translation import ugettext as _
from django import forms

class WPAConfigForm(forms.Form):
    enable = forms.BooleanField(label=_('Enable WPA authentication'), required=False)
    passphrase = forms.CharField(label=_('WPA passphrase'), max_length=100)

