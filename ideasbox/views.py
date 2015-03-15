import urllib2
import mimetypes
import socket

from urlparse import urlparse

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from django.core.validators import URLValidator, ValidationError
from django.forms.models import modelform_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.generic import (ListView, DetailView, UpdateView, CreateView,
                                  DeleteView, View)

from taggit.models import TaggedItem

from ideasbox.blog.models import Content
from ideasbox.library.models import Book
from ideasbox.mediacenter.models import Document

user_model = get_user_model()


def index(request):
    contents = Content.objects.published()[:3]
    random_book = Book.objects.available().order_by('?').first()
    random_doc = Document.objects.order_by('?').first()
    context = {
        'blog_contents': contents,
        'random_book': random_book,
        'random_doc': random_doc,
        'khanacademy_url': settings.KHANACADEMY_URL,
        'wikipedia_url': settings.WIKIPEDIA_URL,
    }
    return render(request, 'index.html', context)


class ByTag(ListView):
    template_name = 'ideasbox/by_tag.html'
    paginate_by = 20

    def get_queryset(self):
        return TaggedItem.objects.filter(tag__slug=self.kwargs['tag'])

by_tag = ByTag.as_view()


class UserList(ListView):
    model = user_model
    template_name = 'ideasbox/user_list.html'
    context_object_name = 'user_list'
user_list = UserList.as_view()


class UserDetail(DetailView):
    model = user_model
    template_name = 'ideasbox/user_detail.html'
    context_object_name = 'user_obj'
user_detail = UserDetail.as_view()


class UserFormMixin(object):
    exclude = ['password', 'last_login']

    def get_form_class(self):
        return modelform_factory(self.model, exclude=self.exclude)


class UserUpdate(UserFormMixin, UpdateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
user_update = staff_member_required(UserUpdate.as_view())


class UserCreate(UserFormMixin, CreateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
user_create = staff_member_required(UserCreate.as_view())


class UserDelete(DeleteView):
    model = user_model
    template_name = 'ideasbox/user_confirm_delete.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('user_list')
user_delete = staff_member_required(UserDelete.as_view())


def validate_url(request):
    assert request.method == "GET"
    assert request.is_ajax()
    url = request.GET.get('url')
    assert url
    try:
        URLValidator(url)
    except ValidationError:
        raise AssertionError()
    assert 'HTTP_REFERER' in request.META
    toproxy = urlparse(url)
    assert toproxy.hostname
    if settings.DEBUG:
        return url
    referer = urlparse(request.META.get('HTTP_REFERER'))
    assert referer.hostname == request.META.get('SERVER_NAME')
    assert toproxy.hostname != "localhost"
    try:
        # clean this when in python 3.4
        ipaddress = socket.gethostbyname(toproxy.hostname)
    except:
        raise AssertionError()
    assert not ipaddress.startswith('127.')
    assert not ipaddress.startswith('192.168.')
    return url


class AjaxProxy(View):

    def get(self, *args, **kwargs):
        # You should not use this in production (use Nginx or so)
        try:
            url = validate_url(self.request)
        except AssertionError as e:
            return HttpResponseBadRequest()
        headers = {
            'User-Agent': 'IdeasBox +http://ideas-box.org'
        }
        request = urllib2.Request(url, headers=headers)
        opener = urllib2.build_opener()
        print(url)
        try:
            proxied_request = opener.open(request)
        except urllib2.HTTPError as e:
            return HttpResponse(e.msg, status=e.code,
                                content_type='text/plain')
        else:
            status_code = proxied_request.code
            mimetype = (proxied_request.headers.typeheader
                        or mimetypes.guess_type(url))
            content = proxied_request.read()
            # Quick hack to prevent Django from adding a Vary: Cookie header
            self.request.session.accessed = False
            return HttpResponse(content, status=status_code,
                                content_type=mimetype)
ajax_proxy = AjaxProxy.as_view()
