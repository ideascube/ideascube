from collections import Counter
import csv
from io import BytesIO, StringIO
from datetime import datetime
from zipfile import ZipFile

from django.conf import settings
from django.conf.locale import LANG_INFO
from django.http import HttpResponse
from taggit.models import Tag


class OrderableViewMixin:

    ORDERS = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.ORDERS:
            default = self.ORDERS[0]
            context['order_by'] = (self.request.GET.get('order_by') or
                                   default['key'])
            context['sort'] = self.request.GET.get('sort') or default['sort']
        return context

    def get_ordering(self):
        if not self.ORDERS:
            return None
        key = self.request.GET.get('order_by')
        for order in self.ORDERS:
            if order['key'] == key:
                break
        else:
            order = self.ORDERS[0]
        order_by = order['expression']
        sort = self.request.GET.get('sort', order['sort'])
        if sort == 'desc':
            order_by = order_by.desc()
        return [order_by]


class FilterableViewMixin:

    def _search_for_attr_from_context(self, attr, context):
        search = {}
        if context.get('q'):
            search['text__match'] = context['q']
        if context.get('kind') and attr != 'kind':
            search['kind'] = context['kind']
        if context.get('lang') and attr != 'lang':
            search['lang'] = context['lang']
        if context.get('source') and attr != 'source':
            search['source'] = context['source']
        if context.get('tags'):
            search['tags__match'] = context['tags']
        return self.model.SearchModel.objects.filter(**search).values_list(attr, flat=True).distinct()

    def _set_available_langs(self, context):
        available_langs = self._search_for_attr_from_context('lang', context)
        context['available_langs'] = [
            (lang, LANG_INFO.get(lang, {}).get('name_local', lang))
            for lang in available_langs]

    def _set_available_tags(self, context):
        all_ = Counter()
        for slugs in self._search_for_attr_from_context('tags', context):
            for slug in slugs.strip('|').split('|'):
                if not slug:
                    continue
                all_[slug] += 1
        common = [slug for slug, count in all_.most_common(20)]
        context['available_tags'] = Tag.objects.filter(slug__in=common)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for key in ('q', 'kind', 'lang', 'source'):
            context[key] = self.request.GET.get(key)
        context['tags'] = self.request.GET.getlist('tags')
        current_filters = [(k, context[k]) for k in ('kind', 'lang', 'source')
                           if context[k]]
        for tag in context['tags']:
            current_filters.append(('tags', tag))
        context['current_filters'] = current_filters

        return context

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q')
        kind = self.request.GET.get('kind')
        lang = self.request.GET.get('lang')
        tags = self.request.GET.getlist('tags')
        source = self.request.GET.get('source')
        if any((query, kind, lang, tags, source)):
            qs = qs.search(text__match=query, lang=lang, kind=kind, tags__match=tags, source=source)
        return qs


class CSVExportMixin:

    content_type = 'text/csv; charset=utf-8'
    file_extension = 'csv'
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

    def get_items(self):
        return self.model.objects.order_by('id')

    def get_headers(self):
        raise NotImplementedError('CSVExportMixin needs a get_headers method')

    def get_row(self, item):
        raise NotImplementedError('CSVExportMixin needs a get_row method')

    def get_filename(self):
        filename = "_".join([
            self.prefix,
            settings.IDEASCUBE_ID,
            str(datetime.now())
        ])
        return filename

    def _get_response_content(self):
        return self.to_csv()

    def get(self, *args, **kwargs):
        response = HttpResponse(self._get_response_content())
        filename = self.get_filename()
        attachment = 'attachment; filename="{name}.{extension}"'.format(
            name=filename, extension=self.file_extension)
        response['Content-Disposition'] = attachment
        response['Content-Type'] = self.content_type
        return response


class ZippedCSVExportMixin(CSVExportMixin):

    content_type = 'application/zip'
    file_extension = 'zip'

    def _get_response_content(self):
        out = BytesIO()

        with ZipFile(out, "a") as self.zip:
            # Warning: Calling to_csv() might write the content of other
            # files to self.zip (through get_row) as a side-effect
            csv = self.to_csv()
            self.zip.writestr("{}.csv".format(self.get_filename()), csv)

        out.seek(0)

        return out.read()
