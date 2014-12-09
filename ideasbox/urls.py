from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ideasbox.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/', include('blog.urls', namespace="blog")),
    url(r'^library/', include('library.urls', namespace="library")),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, kwargs={"next_page": "/"},
        name='logout'),
    url(r'^user/$', views.user_list, name='user_list'),
    url(r'^user/(?P<pk>[\d]+)/$', views.user_detail, name='user_detail'),
    url(r'^user/(?P<pk>[\d]+)/edit/$', views.user_update, name='user_update'),
    url(r'^user/new/$', views.user_create, name='user_create'),
    url(r'^user/(?P<pk>[\d]+)/delete/$',
        views.user_delete, name='user_delete'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
