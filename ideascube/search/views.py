from django.shortcuts import render

from .models import SearchMixin


def search(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        search_kwargs = {'text__match': query}
        if not request.user.is_staff:
            search_kwargs['public'] = True
        for model in SearchMixin.registered_types.values():
            results.extend(model.SearchModel.search(**search_kwargs))
    context = {
        'results': results,
        'q': query
    }
    return render(request, 'search/search.html', context)
