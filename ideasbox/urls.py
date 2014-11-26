from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.admin.views.decorators import staff_member_required
from django.conf.urls import patterns, include, url

from . import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ideasbox.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, kwargs={"next_page": "/"},
        name='logout'),
    url(r'^user/$', views.UserList.as_view(), name='user_list'),
    url(r'^user/(?P<pk>[\d]+)/$',
        views.UserDetail.as_view(), name='user_detail'),
    url(r'^user/(?P<pk>[\d]+)/edit/$',
        staff_member_required(views.UserUpdate.as_view()), name='user_update'),
    url(r'^user/new/$',
        staff_member_required(views.UserCreate.as_view()), name='user_create'),
    url(r'^user/(?P<pk>[\d]+)/delete/$',
        staff_member_required(views.UserDelete.as_view()), name='user_delete'),

    url(r'^admin/', include(admin.site.urls)),
)
