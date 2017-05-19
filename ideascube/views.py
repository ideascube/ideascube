import mimetypes
import socket
from urllib.parse import urlparse
from urllib.request import Request, build_opener
from urllib.error import HTTPError

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.core.urlresolvers import reverse_lazy
from django.core.validators import URLValidator, ValidationError
from django.db import IntegrityError
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect)
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext as _
from django.views.generic import (CreateView, DeleteView, DetailView, FormView,
                                  ListView, UpdateView, View)
from taggit.models import TaggedItem

from ideascube.configuration import get_config
from ideascube.blog.models import Content
from ideascube.decorators import staff_member_required
from ideascube.library.models import Book
from ideascube.mediacenter.models import Document

# For unittesting purpose, we need to mock the Catalog class.
# However, the mock is made in a fixture and at this moment, we don't
# know where the mocked catalog will be used.
# So the fixture mocks 'ideascube.serveradmin.catalog.Catalog'.
# If we want to use the mocked Catalog here, we must not import the
# Catalog class directly but reference it from ideascube.serveradmin.catalog
# module.
from ideascube.serveradmin import catalog as catalog_mod

from .forms import UserForm, CreateStaffForm, UserImportForm
from .mixins import CSVExportMixin

user_model = get_user_model()


def build_package_card_info():
    package_card_info = []
    catalog = catalog_mod.Catalog()
    packages_to_display = catalog.list_installed(get_config('home-page', 'displayed-package-ids'))

    for package in packages_to_display:
        card_info = {
            'id': package.template_id,
            'name': package.name,
            'description': getattr(package, 'description', ''),
            'lang': getattr(package, 'language', ''),
            'package_id': package.id,
            'is_staff': getattr(package, 'staff_only', False),
            'theme': getattr(package, 'theme', None),
            'css_class': getattr(package, 'css_class', None)
        }
        package_card_info.append(card_info)
    return package_card_info


def index(request):
    if not user_model.objects.filter(is_staff=True).exists():
        return HttpResponseRedirect(reverse_lazy('welcome_staff'))
    content = Content.objects.published().order_by('published_at').first()
    random_book = Book.objects.available().order_by('?').first()
    random_doc = Document.objects.order_by('?').first()

    staff_cards = settings.STAFF_HOME_CARDS
    builtin_cards = settings.BUILTIN_APP_CARDS
    extra_cards = settings.EXTRA_APP_CARDS
    custom_cards = settings.CUSTOM_CARDS
    package_cards = build_package_card_info()

    cards = staff_cards + builtin_cards + extra_cards + package_cards

    context = {
        'blog_content': content,
        'random_book': random_book,
        'random_doc': random_doc,
        'cards': cards,
    }
    return render(request, 'index.html', context)


def welcome_staff(request):
    """Allow to create a staff user if None exists yet."""
    if user_model.objects.filter(is_staff=True).exists():
        return HttpResponseRedirect('/')
    if request.method == 'POST':
        form = CreateStaffForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(serial=user.serial,
                                password=request.POST['password'])
            login(request, user)
            msg = _(u'Welcome to {}, {}!').format(
                get_config('server', 'site-name'), user)
            messages.add_message(request, messages.SUCCESS, msg)
            return HttpResponseRedirect('/')
    else:
        form = CreateStaffForm()
    return render(request, 'ideascube/welcome_staff.html', {'form': form})


class ByTag(ListView):
    template_name = 'ideascube/by_tag.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = self.request.GET.getlist('tags')
        return context

    def get_queryset(self):
        tags = self.request.GET.getlist('tags')
        return TaggedItem.objects.filter(tag__slug__in=tags).distinct()

by_tag = ByTag.as_view()


class UserList(ListView):
    model = user_model
    template_name = 'ideascube/user_list.html'
    context_object_name = 'user_list'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['USERS_LIST_EXTRA_FIELDS'] = settings.USERS_LIST_EXTRA_FIELDS
        context['q'] = self.request.GET.get('q', '')
        return context

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return self.model.objects.search(query)
        else:
            return super().get_queryset()

user_list = staff_member_required(UserList.as_view())


class UserDetail(DetailView):
    model = user_model
    template_name = 'ideascube/user_detail.html'
    context_object_name = 'user_obj'
user_detail = staff_member_required(UserDetail.as_view())


class UserFormMixin(object):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['USER_FORM_FIELDS'] = settings.USER_FORM_FIELDS
        return context


class UserUpdate(UserFormMixin, UpdateView):
    model = user_model
    template_name = 'ideascube/user_form.html'
    context_object_name = 'user_obj'
    form_class = UserForm
user_update = staff_member_required(UserUpdate.as_view())


class UserCreate(UserFormMixin, CreateView):
    model = user_model
    template_name = 'ideascube/user_form.html'
    context_object_name = 'user_obj'
    form_class = UserForm
user_create = staff_member_required(UserCreate.as_view())


class UserDelete(DeleteView):
    model = user_model
    template_name = 'ideascube/user_confirm_delete.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('user_list')

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except IntegrityError as e:
            messages.add_message(request, messages.ERROR, e.args[0])
            return HttpResponseRedirect(self.object.get_absolute_url())

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
    template_name = 'ideascube/set_password.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = get_object_or_404(user_model, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        form.save()
        msg = _('Password has been set for {user}').format(user=form.user)
        messages.add_message(self.request, messages.SUCCESS, msg)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('user_detail', kwargs=self.kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['user'] = context['form'].user
        return context

set_password = staff_member_required(SetPassword.as_view())


class UserExport(CSVExportMixin, View):

    model = user_model

    def get_headers(self):
        fields = user_model.get_data_fields()
        self.fields = [f for f in fields if f.name not in user_model.PRIVATE_DATA]
        return [f.name for f in self.fields]

    def get_row(self, user):
        data_fields = user.data_fields
        row = {}
        for field in self.fields:
            value = data_fields[field.name]['value']
            if value is None:
                value = ''
            value = str(value)
            row[field.name] = value
        return row
user_export = staff_member_required(UserExport.as_view())


class UserImport(FormView):
    form_class = UserImportForm
    template_name = 'ideascube/user_import.html'
    success_url = reverse_lazy('user_import')

    def form_valid(self, form):
        users, errors = form.save()
        if users:
            msg = _('Successfully processed {count} users.')
            msg = msg.format(count=len(users))
            messages.success(self.request, msg)
        for error in errors:
            messages.error(self.request, error)
        return super().form_valid(form)

user_import = staff_member_required(UserImport.as_view())


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
            'User-Agent': 'ideascube +http://ideas-box.org'
        }
        request = Request(url, headers=headers)
        opener = build_opener()
        try:
            proxied_request = opener.open(request)
        except HTTPError as e:
            return HttpResponse(e.msg, status=e.code,
                                content_type='text/plain')
        else:
            status_code = proxied_request.code
            mimetype = proxied_request.headers.get('Content-Type') or mimetypes.guess_type(url)  # noqa
            content = proxied_request.read()
            # Quick hack to prevent Django from adding a Vary: Cookie header
            self.request.session.accessed = False
            return HttpResponse(content, status=status_code,
                                content_type=mimetype)
ajax_proxy = AjaxProxy.as_view()
