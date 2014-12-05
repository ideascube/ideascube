from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^server/$', views.server, name='server'),
    url(r'^services/$', views.services, name='services'),
)
