from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .models import Document
from .forms import DocumentForm


class Index(ListView):
    model = Document
    template_name = 'mediacenter/index.html'
    paginate_by = 10
index = Index.as_view()


class DocumentDetail(DetailView):
    model = Document
document_detail = DocumentDetail.as_view()


class DocumentUpdate(UpdateView):
    model = Document
    form_class = DocumentForm
document_update = staff_member_required(DocumentUpdate.as_view())


class DocumentCreate(CreateView):
    model = Document
    form_class = DocumentForm
    initial = {
        'lang': settings.LANGUAGE_CODE,
    }
document_create = staff_member_required(DocumentCreate.as_view())


class DocumentDelete(DeleteView):
    model = Document
    success_url = reverse_lazy('mediacenter:index')
document_delete = staff_member_required(DocumentDelete.as_view())
