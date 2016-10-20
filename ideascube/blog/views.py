from django.views.generic import (ListView, DetailView, UpdateView, CreateView)
from django.db.models import F
from django.utils.translation import ugettext_lazy as _

from ideascube.mixins import FilterableViewMixin, OrderableViewMixin
from ideascube.decorators import staff_member_required

from .forms import ContentForm
from .models import Content


class Index(FilterableViewMixin, OrderableViewMixin, ListView):

    ORDERS = [
        {
            'key': 'published_at',
            'label': _('Last published'),
            'expression': F('published_at'),
            'sort': 'desc'
        }
    ]

    model = Content
    queryset = Content.objects.published()
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self._set_available_langs(context)
        self._set_available_tags(context)
        return context

index = Index.as_view()


class ContentDetail(DetailView):
    model = Content

    def get_queryset(self):
        if self.request.user.is_authenticated() and self.request.user.is_staff:
            return Content.objects.all()
        else:
            return Content.objects.published()

content_detail = ContentDetail.as_view()


class ContentUpdate(UpdateView):
    model = Content
    form_class = ContentForm
content_update = staff_member_required(ContentUpdate.as_view())


class ContentCreate(CreateView):
    model = Content
    form_class = ContentForm

    def get_initial(self):
        initial = super(ContentCreate, self).get_initial()
        initial['author'] = self.request.user
        return initial
content_create = staff_member_required(ContentCreate.as_view())
