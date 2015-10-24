from django.views.generic import ListView

from taggit.models import Tag


class ByTagListView(ListView):

    def get_queryset(self):
        qs = super(ByTagListView, self).get_queryset()
        if 'tag' in self.kwargs:
            qs = qs.filter(tags__slug__in=[self.kwargs['tag']])
        return qs

    def get_context_data(self, **kwargs):
        context = super(ByTagListView, self).get_context_data(**kwargs)
        context['tag'] = Tag.objects.get(slug=self.kwargs.get('tag'))
        return context
