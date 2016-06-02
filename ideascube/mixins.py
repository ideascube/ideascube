import csv
from io import StringIO
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import ListView

from taggit.models import Tag


class FilterableViewMixin:
    def _search_for_attr_from_context(self, attr, context):
        search_context = {k:context[k] for k in ('q', 'kind', 'lang', 'tags')
                            if k != attr}
        try:
            search_context['query'] = search_context.pop('q')
        except KeyError:
            pass
        existing_attrs = set(self.model.objects
                                .search(**search_context)
                                .values_list(attr, flat=True)
                             )
        return existing_attrs


    def get_context_data(self, **kwargs):
        context = super(FilterableViewMixin, self).get_context_data(**kwargs)
        for key in ('q', 'kind', 'lang'):
            context[key] = self.request.GET.get(key)
        context['tags'] = self.request.GET.getlist('tags')
        default_values = {k: context[k] for k in ('kind', 'lang', 'tags')
                          if context[k]}
        context['default_values'] = default_values

        return context

    def get_queryset(self):
        qs = super(FilterableViewMixin, self).get_queryset()
        query = self.request.GET.get('q')
        kind = self.request.GET.get('kind')
        lang = self.request.GET.get('lang')
        tags = self.request.GET.getlist('tags')

        if any((query, kind, lang, tags)):
            qs = qs.search(query=query, lang=lang, kind=kind, tags=tags)
        return qs


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
