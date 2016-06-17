from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page
from django.views.i18n import javascript_catalog

from . import views

urlpatterns = i18n_patterns(
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/', include('ideascube.blog.urls', namespace="blog")),
    url(r'^library/', include('ideascube.library.urls', namespace="library")),
    url(r'^search/', include('ideascube.search.urls', namespace="search")),
    url(r'^mediacenter/', include('ideascube.mediacenter.urls',
                                  namespace="mediacenter")),
    url(r'^monitoring/', include('ideascube.monitoring.urls',
                                 namespace="monitoring")),
    url(r'^$', views.index, name='index'),
    url(r'^welcome_staff/$', views.welcome_staff, name='welcome_staff'),
    url(r'^tag/$', views.by_tag, name='by_tag'),
    url(r'^server/', include('ideascube.serveradmin.urls', namespace="server")),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, kwargs={"next_page": "/"},
        name='logout'),
    url(r'^user/$', views.user_list, name='user_list'),
    url(r'^user/(?P<pk>[\d]+)/$', views.user_detail, name='user_detail'),
    url(r'^user/(?P<pk>[\d]+)/edit/$', views.user_update, name='user_update'),
    url(r'^user/(?P<pk>[\d]+)/set-password/$', views.set_password,
        name='user_set_password'),
    url(r'^user/new/$', views.user_create, name='user_create'),
    url(r'^user/export/$', views.user_export, name='user_export'),
    url(r'^user/(?P<pk>[\d]+)/delete/$',
        views.user_delete, name='user_delete'),
    url(r'^user/(?P<pk>[\d]+)/toggle-staff/$',
        views.user_toggle_staff, name='user_toggle_staff'),
    url(r'^js/$', views.javascript, name='javascript'),
    url(r'^ajax-proxy/$', cache_page(180)(views.ajax_proxy), name='ajax-proxy')
)
urlpatterns = urlpatterns + [
    url(r'^jsi18n/$', javascript_catalog),
    url(r'^i18n/', include('django.conf.urls.i18n')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
