from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import BookForm, BookSpecimenForm
from .models import Book, BookSpecimen


class Index(ListView):
    model = Book
    queryset = Book.objects.available()
    template_name = 'library/index.html'
    paginate_by = 10
index = Index.as_view()


class BookDetail(DetailView):
    model = Book
book_detail = BookDetail.as_view()


class BookUpdate(UpdateView):
    model = Book
    form_class = BookForm
book_update = staff_member_required(BookUpdate.as_view())


class BookCreate(CreateView):
    model = Book
    form_class = BookForm
    initial = {
        'lang': settings.LANGUAGE_CODE,
        'location': settings.IDEASBOX_ID
    }
book_create = staff_member_required(BookCreate.as_view())


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('library:index')
book_delete = staff_member_required(BookDelete.as_view())


class SpecimenCreate(CreateView):
    model = BookSpecimen
    form_class = BookSpecimenForm
    template_name = 'library/specimen_form.html'

    def get_initial(self):
        book = get_object_or_404(Book, pk=self.kwargs['book_pk'])
        return {'book': book}

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
