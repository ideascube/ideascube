from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^power/$', views.power, name='power'),
    url(r'^services/$', views.services, name='services'),
    url(r'^backup/$', views.backup, name='backup'),
    url(r'^battery/$', views.battery, name='battery'),
]