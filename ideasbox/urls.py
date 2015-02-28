from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page

from . import views

urlpatterns = i18n_patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/', include('ideasbox.blog.urls', namespace="blog")),
    url(r'^library/', include('ideasbox.library.urls', namespace="library")),
    url(r'^search/', include('ideasbox.search.urls', namespace="search")),
    url(r'^mediacenter/', include('ideasbox.mediacenter.urls',
                                  namespace="mediacenter")),
    url(r'^$', views.index, name='index'),
    url(r'^server/', include('ideasbox.serveradmin.urls', namespace="server")),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, kwargs={"next_page": "/"},
        name='logout'),
    url(r'^user/$', views.user_list, name='user_list'),
    url(r'^user/(?P<pk>[\d]+)/$', views.user_detail, name='user_detail'),
    url(r'^user/(?P<pk>[\d]+)/edit/$', views.user_update, name='user_update'),
    url(r'^user/new/$', views.user_create, name='user_create'),
    url(r'^user/(?P<pk>[\d]+)/delete/$',
        views.user_delete, name='user_delete'),
    url(r'^ajax-proxy/$', cache_page(180)(views.ajax_proxy), name='ajax-proxy'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [url(r'^i18n/', include('django.conf.urls.i18n')),]
