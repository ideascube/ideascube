from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^book/(?P<pk>[\d]+)/$', views.book_detail, name='book_detail'),
    url(r'^book/(?P<pk>[\d]+)/edit/$', views.book_update, name='book_update'),
    url(r'^book/(?P<pk>[\d]+)/delete/$', views.book_delete,
        name='book_delete'),
    url(r'^book/new/$', views.book_create, name='book_create'),
    url(r'^book/export/$', views.book_export, name='book_export'),
    url(r'^book/import/$', views.book_import, name='book_import'),
    url(r'^book/(?P<book_pk>[\d]+)/new-specimen/$', views.specimen_create,
        name='specimen_create'),
    url(r'^specimen/(?P<pk>[\d]+)/edit/$', views.specimen_update,
        name='specimen_update'),
    url(r'^specimen/(?P<pk>[\d]+)/delete/$', views.specimen_delete,
        name='specimen_delete'),
]
