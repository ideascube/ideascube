import json

from urllib.parse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse_lazy, resolve, Resolver404
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from ideascube.decorators import staff_member_required

from .models import Document
from .forms import DocumentForm


class Index(ListView):
    model = Document
    template_name = 'mediacenter/index.html'
    paginate_by = 24

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        for key in ('q', 'kind', 'lang'):
            context[key] = self.request.GET.get(key)
        context['tags'] = self.request.GET.getlist('tags')
        default_values = {k: context[k] for k in ('kind', 'lang', 'tags')
                          if context[k]}
        context['default_values'] = default_values
        context['not_empty_kinds'] = [
            (kind, label) for kind, label in Document.KIND_CHOICES
            if len(Document.objects.filter(kind=kind))
            ]
        context['not_empty_langs'] = [
            (lang, label) for lang, label in settings.LANGUAGES
            if len(Document.objects.filter(lang=lang))
            ]
        return context

    def get_queryset(self):
        qs = super(Index, self).get_queryset()
        query = self.request.GET.get('q')
        kind = self.request.GET.get('kind')
        lang = self.request.GET.get('lang')
        tags = self.request.GET.getlist('tags')
        if any((query, kind, lang, tags)):
            return qs.search(query=query, lang=lang, kind=kind, tags=tags)
        return qs

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


class OEmbed(DetailView):
    model = Document
    content_type = 'application/json'
    template_name = 'mediacenter/oembed.html'

    def get_object(self, queryset=None):
        if not queryset:
            queryset = self.get_queryset()
        url = self.request.GET.get('url')
        if not url:
            raise Http404()
        parsed = urlparse(url)
        try:
            match = resolve(parsed.path)
        except Resolver404:
            raise Http404()
        if 'pk' not in match.kwargs:
            raise Http404()
        return queryset.get(pk=match.kwargs['pk'])

    def render_to_response(self, context, **response_kwargs):
        response_kwargs.setdefault('content_type', self.content_type)
        html = render_to_string(self.get_template_names(), response_kwargs,
                                RequestContext(self.request, context))
        return HttpResponse(json.dumps({
            "html": html,
            "type": "rich"
        }))

oembed = OEmbed.as_view()
