from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView, View)
from ideasbox.mixins import ByTagListView
from ideasbox.views import CSVExportMixin

from .forms import BookForm, BookSpecimenForm, ImportForm
from .models import Book, BookSpecimen


class Index(ListView):
    model = Book
    queryset = Book.objects.available()
    template_name = 'library/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.search(query)
        else:
            return super(Index, self).get_queryset().order_by('-modified_at')

index = Index.as_view()


class ByTag(ByTagListView):
    model = Book
    queryset = Book.objects.available()
    template_name = 'library/by_tag.html'
    paginate_by = 10

by_tag = ByTag.as_view()


class BookDetail(DetailView):
    model = Book
book_detail = BookDetail.as_view()

class BookExport(CSVExportMixin, View):

    """
    Book model export class using seralizable Django model
    """

    def get(self, *args, **kwargs):
        return self.render_to_csv()

    def get_items(self):
        return Book.objects.all()

    def get_headers(self):
        self.fields = Book.get_data_fields()
        return [unicode(f.verbose_name).encode('utf-8') for f in self.fields]

    def get_row(self, book):
        data_fields = book.to_data_array()
        row = {}
        for x, field in enumerate(self.fields):
            value = unicode(field).encode('utf-8')
            row[unicode(field.verbose_name).encode('utf-8')] = data_fields[x]
        return row

book_export = staff_member_required(BookExport.as_view())


class BookUpdate(UpdateView):
    model = Book
    form_class = BookForm
book_update = staff_member_required(BookUpdate.as_view())


class BookCreate(CreateView):
    model = Book
    form_class = BookForm
    initial = {
        'lang': settings.LANGUAGE_CODE
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
            except ValueError:
                msg = _('Unable to process notices.')
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
        return {'book': book, 'location': settings.IDEASBOX_NAME}

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
