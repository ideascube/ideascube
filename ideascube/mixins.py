import csv
from io import StringIO
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView

from taggit.models import Tag


class ByTagListView(ListView):

    def get_queryset(self):
        qs = super(ByTagListView, self).get_queryset()
        if 'tag' in self.kwargs:
            qs = qs.filter(tags__slug__in=[self.kwargs['tag']])
        return qs

    def get_context_data(self, **kwargs):
        context = super(ByTagListView, self).get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(slug=self.kwargs.get('tag'))
        return context


class CSVExportMixin(object):

    prefix = 'ideascube'

    def to_csv(self):
        out = StringIO()
        headers = self.get_headers()
        writer = csv.DictWriter(out, headers)
        writer.writeheader()
        for item in self.get_items():
            row = self.get_row(item)
            writer.writerow(row)
        out.seek(0)
        return out.read()

    def render_to_csv(self):
        response = HttpResponse(self.to_csv())
        filename = self.get_filename()
        attachment = 'attachment; filename="{name}.csv"'.format(name=filename)
        response['Content-Disposition'] = attachment
        response['Content-Type'] = 'text/csv'
        return response

    def get_item(self):
        raise NotImplementedError('CSVExportMixin needs a get_items method')

    def get_headers(self):
        raise NotImplementedError('CSVExportMixin needs a get_headers method')

    def get_filename(self):
        filename = "_".join([
            self.prefix,
            settings.IDEASCUBE_ID,
            str(datetime.now())
        ])
        return filename
