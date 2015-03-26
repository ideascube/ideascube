import csv
import mimetypes
import socket
import StringIO
import urllib2
from datetime import datetime
from urlparse import urlparse

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.core.urlresolvers import reverse_lazy
from django.core.validators import URLValidator, ValidationError
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView, View)
from taggit.models import TaggedItem

from ideasbox.blog.models import Content
from ideasbox.library.models import Book
from ideasbox.mediacenter.models import Document

from .forms import UserForm

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
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context['USERS_LIST_EXTRA_FIELDS'] = settings.USERS_LIST_EXTRA_FIELDS
        context['q'] = self.request.GET.get('q', '')
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.search(query)
        else:
            return super(UserList, self).get_queryset()

user_list = staff_member_required(UserList.as_view())


class UserDetail(DetailView):
    model = user_model
    template_name = 'ideasbox/user_detail.html'
    context_object_name = 'user_obj'
user_detail = staff_member_required(UserDetail.as_view())


class UserUpdate(UpdateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
    form_class = UserForm
user_update = staff_member_required(UserUpdate.as_view())


class UserCreate(CreateView):
    model = user_model
    template_name = 'ideasbox/user_form.html'
    context_object_name = 'user_obj'
    form_class = UserForm
user_create = staff_member_required(UserCreate.as_view())


class UserDelete(DeleteView):
    model = user_model
    template_name = 'ideasbox/user_confirm_delete.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('user_list')
user_delete = staff_member_required(UserDelete.as_view())


class UserToggleStaff(View):

    def get(self, *args, **kwargs):
        self.user = get_object_or_404(user_model, pk=self.kwargs['pk'])
        self.user.is_staff = not self.user.is_staff
        self.user.save()
        return HttpResponseRedirect(self.user.get_absolute_url())
user_toggle_staff = staff_member_required(UserToggleStaff.as_view())


class SetPassword(FormView):
    form_class = SetPasswordForm
    template_name = 'ideasbox/set_password.html'

    def get_form_kwargs(self):
        kwargs = super(SetPassword, self).get_form_kwargs()
        kwargs['user'] = get_object_or_404(user_model, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.save()
        msg = _('Password has been set for {user}').format(user=form.user)
        messages.add_message(self.request, messages.SUCCESS, msg)
        return super(SetPassword, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs=self.kwargs)

set_password = staff_member_required(SetPassword.as_view())


@staff_member_required
def user_export(request):
    out = StringIO.StringIO()
    fields = user_model.get_public_fields()
    headers = [unicode(f.verbose_name).encode('utf-8') for f in fields]
    writer = csv.DictWriter(out, headers)
    writer.writeheader()
    qs = user_model.objects.all()
    for user in qs:
        public_fields = user.public_fields
        row = {}
        for field in fields:
            value = public_fields[field.name]['value']
            if value is None:
                value = ''
            value = unicode(value).encode('utf-8')
            row[unicode(field.verbose_name).encode('utf-8')] = value
        writer.writerow(row)
    out.seek(0)
    response = HttpResponse(out.read())
    filename = 'users_{id}_{date}'.format(id=settings.IDEASBOX_ID,
                                          date=datetime.now())
    attachment = 'attachment; filename="{name}.csv"'.format(
        name=filename)
    response['Content-Disposition'] = attachment
    response['Content-Type'] = 'text/csv'
    return response


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
