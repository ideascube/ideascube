from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^entry/export/$', views.export_entry, name='export_entry'),
]
