from django.views.generic import (ListView, DetailView, UpdateView, CreateView)

from ideascube.mixins import ByTagListView
from ideascube.decorators import staff_member_required

from .forms import ContentForm
from .models import Content


class Index(ListView):
    model = Content
    queryset = Content.objects.published()
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        context['tags'] = self.request.GET.getlist('tags')
        context['default_values'] = {'tags': context['tags']}
        return context

    def get_queryset(self):
        qs = super(Index, self).get_queryset()
        tags = self.request.GET.getlist('tags')
        if tags:
            return qs.search(tags=tags)
        return qs

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
content_create = staff_member_required(ContentCreate.as_view())
