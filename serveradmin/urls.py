from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^power/$', views.power, name='power'),
    url(r'^services/$', views.services, name='services'),
)
