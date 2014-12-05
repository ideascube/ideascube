from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^server/$', views.server, name='server'),
)
