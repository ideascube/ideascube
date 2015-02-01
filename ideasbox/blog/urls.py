from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<pk>[\d]+)/$', views.content_detail, name='content_detail'),
    url(r'^(?P<pk>[\d]+)/edit/$', views.content_update, name='content_update'),
    url(r'^new/$', views.content_create, name='content_create'),
]
