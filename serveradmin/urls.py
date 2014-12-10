from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^services/$', views.services, name='services'),
)
