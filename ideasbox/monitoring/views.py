import csv
import StringIO

from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from .forms import EntryForm, ExportEntryForm
from .models import Entry

user_model = get_user_model()


class EntryView(FormView):
    template_name = 'monitoring/entry.html'
    form_class = EntryForm
    success_url = reverse_lazy('monitoring:entry')

    def form_valid(self, form):
        count = 0
        module = form.cleaned_data['module']
        for serial in form.cleaned_data['serials']:
            try:
                user = user_model.objects.get(serial=serial)
            except user_model.DoesNotExist:
                msg = _('No user found with serial {serial}')
                msg = msg.format(serial=serial)
                messages.add_message(self.request, messages.ERROR, msg)
            else:
                Entry.objects.create(user=user, module=module)
                count += 1
        if count:
            msg = _('Created {count} entries')
            msg = msg.format(count=count)
            messages.add_message(self.request, messages.SUCCESS, msg)
        else:
            msg = _('No entry created.')
            messages.add_message(self.request, messages.WARNING, msg)
        return super(EntryView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(EntryView, self).get_context_data(**kwargs)
        context['entries'] = Entry.objects.all()[:20]
        context['export_form'] = ExportEntryForm()
        return context

entry = staff_member_required(EntryView.as_view())


@staff_member_required
def export_entry(request):
    form = ExportEntryForm(request.GET)
    if form.is_valid():
        out = StringIO.StringIO()
        fields = ['module', 'date']
        fields.extend(settings.MONITORING_ENTRY_EXPORT_FIELDS)
        writer = csv.DictWriter(out, fields)
        writer.writeheader()
        qs = Entry.objects.all()
        if form.cleaned_data['since']:
            qs = qs.filter(created_at__gte=form.cleaned_data['since'])
        for entry in qs:
            row = {'module': entry.module, 'date': entry.created_at}
            for field in settings.MONITORING_ENTRY_EXPORT_FIELDS:
                row[field] = getattr(entry.user, field, None)
            writer.writerow(row)
        out.seek(0)
        response = HttpResponse(out.read())
        filename = 'entries_{id}_{date}'.format(id=settings.IDEASBOX_ID,
                                                date=datetime.now())
        attachment = 'attachment; filename="{name}.csv"'.format(
            name=filename)
        response['Content-Disposition'] = attachment
        response['Content-Type'] = 'text/csv'
        return response
