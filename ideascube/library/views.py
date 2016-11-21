import os
from io import BytesIO
from zipfile import ZipFile

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.db.models import F
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils.translation import get_language, ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView, View)

from ideascube.configuration import get_config
from ideascube.decorators import staff_member_required
from ideascube.mixins import (FilterableViewMixin, CSVExportMixin,
                              OrderableViewMixin)

from .forms import BookForm, BookSpecimenForm, ImportForm
from .models import Book, BookSpecimen


class Index(FilterableViewMixin, OrderableViewMixin, ListView):

    ORDERS = [
        {
            'key': 'created_at',
            'label': _('Last added'),
            'expression': F('created_at'),
            'sort': 'desc'
        },
        {
            'key': 'name',
            'label': _('Title'),
            'expression': Lower('name'),  # Case insensitive.
            'sort': 'asc'
        },
        {
            'key': 'authors',
            'label': _('Author'),
            'expression': Lower('authors'),  # Case insensitive.
            'sort': 'asc'
        }
    ]

    model = Book
    template_name = 'library/index.html'
    paginate_by = 10

    def _set_available_kinds(self, context):
        available_kinds = self._search_for_attr_from_context('kind', context)
        context['available_kinds'] = [
            (kind, label) for kind, label in Book.SECTION_CHOICES
            if kind in available_kinds]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not (user.is_authenticated() and user.is_staff):
            qs = qs.filter(specimens__isnull=False).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        self._set_available_langs(context)
        self._set_available_tags(context)
        self._set_available_kinds(context)
        return context

index = Index.as_view()


class BookDetail(DetailView):
    model = Book

    def get(self, request, *args, **kwargs):
        ret = super().get(request, *args, **kwargs)
        user = request.user
        if user.is_staff and not self.object.specimens.count():
            messages.warning(request, _("Please add a specimen, or the book "
                                        "won't be available for the users"))
        return ret
book_detail = BookDetail.as_view()


class BookUpdate(UpdateView):
    model = Book
    form_class = BookForm
book_update = staff_member_required(BookUpdate.as_view())


class BookCreate(CreateView):
    model = Book
    form_class = BookForm
    initial = {
        'lang': get_language()
    }
book_create = staff_member_required(BookCreate.as_view())


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('library:index')
book_delete = staff_member_required(BookDelete.as_view())


class BookImport(FormView):
    form_class = ImportForm
    template_name = 'library/import.html'
    success_url = reverse_lazy('library:book_import')

    def form_valid(self, form):
        handler = None
        if form.cleaned_data['from_files']:
            handler = form.save_from_files
        elif form.cleaned_data['from_isbn']:
            handler = form.save_from_isbn
        if handler:
            try:
                notices = handler()
            except (ValueError, AssertionError) as e:
                msg = _(u'Unable to process notices: {}'.format(str(e)))
                messages.add_message(self.request, messages.ERROR, msg)
            else:
                if notices:
                    msg = _('Successfully processed {count} notices.')
                    msg = msg.format(count=len(notices))
                    messages.add_message(self.request, messages.SUCCESS, msg)
                    if len(notices) == 1:
                        self.success_url = notices[0].get_absolute_url()
                else:
                    msg = _('No notice processed')
                    messages.add_message(self.request, messages.INFO, msg)
        else:
            msg = _('You need to provide a file.')
            messages.add_message(self.request, messages.ERROR, msg)
        return super(BookImport, self).form_valid(form)

book_import = staff_member_required(BookImport.as_view())


class SpecimenCreate(CreateView):
    model = BookSpecimen
    form_class = BookSpecimenForm
    template_name = 'library/specimen_form.html'

    def get_initial(self):
        book = get_object_or_404(Book, pk=self.kwargs['book_pk'])

        return {'item': book, 'location': get_config('server', 'site-name')}

specimen_create = staff_member_required(SpecimenCreate.as_view())


class SpecimenUpdate(UpdateView):
    model = BookSpecimen
    form_class = BookSpecimenForm
    context_object_name = 'specimen'
    template_name = 'library/specimen_form.html'
specimen_update = staff_member_required(SpecimenUpdate.as_view())


class SpecimenDelete(DeleteView):
    model = BookSpecimen
    context_object_name = 'specimen'
    template_name = 'library/specimen_confirm_delete.html'

    def get_success_url(self):
        return self.object.get_absolute_url()

specimen_delete = staff_member_required(SpecimenDelete.as_view())


class BookExport(CSVExportMixin, View):

    prefix = 'notices'
    fields = ['isbn', 'authors', 'serie', 'name', 'subtitle', 'description',
              'publisher', 'section', 'lang', 'cover', 'tags']

    def get(self, *args, **kwargs):
        out = BytesIO()
        self.zip = ZipFile(out, "a")
        csv = self.to_csv()
        self.zip.writestr("{}.csv".format(self.get_filename()), csv)
        self.zip.close()
        response = HttpResponse()
        filename = self.get_filename()
        attachment = 'attachment; filename="{name}.zip"'.format(name=filename)
        response['Content-Disposition'] = attachment
        response['Content-Type'] = 'application/zip'
        out.seek(0)
        response.write(out.read())
        return response

    def get_items(self):
        return Book.objects.all()

    def get_headers(self):
        return self.fields

    def get_row(self, book):
        row = {}
        for name in self.fields:
            if name == 'tags':
                value = ','.join(book.tags.names())
            else:
                value = getattr(book, name, None) or ''

            if not isinstance(value, str):
                value = str(value)

            row[name] = value
        if book.cover:
            path, ext = os.path.splitext(book.cover.name)
            filename = '{}{}'.format(book.pk, ext)
            row['cover'] = filename
            self.zip.writestr(filename, book.cover.read())
        return row

book_export = staff_member_required(BookExport.as_view())
