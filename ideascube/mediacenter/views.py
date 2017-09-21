from django.core.urlresolvers import reverse_lazy
from django.db.models import F
from django.db.models.functions import Lower
from django.utils.translation import get_language, ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.core.exceptions import PermissionDenied

from ideascube.decorators import staff_member_required
from ideascube.mixins import FilterableViewMixin, OrderableViewMixin

# For unittesting purpose, we need to mock the Catalog class.
# However, the mock is made in a fixture and at this moment, we don't
# know where the mocked catalog will be used.
# So the fixture mocks 'ideascube.serveradmin.catalog.Catalog'.
# If we want to use the mocked Catalog here, we must not import the
# Catalog class directly but reference it from ideascube.serveradmin.catalog
# module.
from ideascube.serveradmin import catalog as catalog_mod

from .models import Document
from .forms import CreateDocumentForm, DocumentForm


class NoHiddenDocumentMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(hidden=False)
        return qs


class Index(NoHiddenDocumentMixin, FilterableViewMixin, OrderableViewMixin, ListView):

    ORDERS = [
        {
            'key': 'modified_at',
            'label': _('Last modification'),
            'expression': F('modified_at'),
            'sort': 'desc'
        },
        {
            'key': 'title',
            'label': _('Title'),
            'expression': Lower('title'),  # Case insensitive.
            'sort': 'asc'
        }
    ]

    model = Document
    template_name = 'mediacenter/index.html'
    paginate_by = 24

    def _set_available_kinds(self, context):
        available_kinds = self._search_for_attr_from_context('kind', context)
        context['available_kinds'] = [
            (kind, label) for kind, label in Document.KIND_CHOICES
            if kind in available_kinds]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._set_available_kinds(context)
        self._set_available_langs(context)
        self._set_available_tags(context)
        # We assume that if there is a source, it is a package_id.
        package_id = context.get('source')
        if package_id:
            catalog = catalog_mod.Catalog()
            try:
                package = catalog.list_installed([package_id])[0]
            except IndexError:
                # We cannot find the package.
                # This should not happen. Remove the filter
                del context['source']
                return context

            context['source_name'] = package.name
        return context
index = Index.as_view()

class DocumentSelect(Index):
    template_name = 'mediacenter/document_select.html'
document_select = DocumentSelect.as_view()


class DocumentDetail(NoHiddenDocumentMixin, DetailView):
    model = Document
document_detail = DocumentDetail.as_view()


class DocumentUpdate(NoHiddenDocumentMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    def get_object(self, *args, **kwargs):
        object = super().get_object(*args, **kwargs)
        if object.package_id:
            raise PermissionDenied
        return object
document_update = staff_member_required(DocumentUpdate.as_view())


class DocumentCreate(CreateView):
    model = Document
    form_class = CreateDocumentForm
    initial = {
        'lang': get_language(),
    }
document_create = staff_member_required(DocumentCreate.as_view())


class DocumentDelete(NoHiddenDocumentMixin, DeleteView):
    model = Document
    success_url = reverse_lazy('mediacenter:index')
    def get_object(self, *args, **kwargs):
        object = super().get_object(*args, **kwargs)
        if object.package_id:
            raise PermissionDenied
        return object
document_delete = staff_member_required(DocumentDelete.as_view())
