from django.conf.urls import url

from . import views


app_name = 'mediacenter'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^select/$', views.document_select, name='document_select'),
    url(r'^document/(?P<pk>[\d]+)/$', views.document_detail,
        name='document_detail'),
    url(r'^document/(?P<pk>[\d]+)/edit/$', views.document_update,
        name='document_update'),
    url(r'^document/(?P<pk>[\d]+)/delete/$', views.document_delete,
        name='document_delete'),
    url(r'^document/new/$', views.document_create, name='document_create'),
]
