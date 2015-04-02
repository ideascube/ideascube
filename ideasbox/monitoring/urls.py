from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^entry/$', views.entry, name='entry'),
    url(r'^entry/export/$', views.export_entry, name='export_entry'),
    url(r'^stock/$', views.stock, name='stock'),
    url(r'^stock/inventory/(?P<pk>[\d]+)/$', views.inventory, name='inventory'),  # noqa
    url(r'^stock/inventory/(?P<pk>[\d]+)/edit/$', views.inventory_update, name='inventory_update'),  # noqa
    url(r'^stock/inventory/(?P<pk>[\d]+)/export/$', views.inventory_export, name='inventory_export'),  # noqa
    url(r'^inventory/(?P<pk>[\d]+)/delete/$', views.inventory_delete, name='inventory_delete'),  # noqa
    url(r'^stock/inventory/new/$', views.inventory_create, name='inventory_create'),  # noqa
    url(r'^stock/item/(?P<pk>[\d]+)/edit/$', views.stockitem_update, name='stockitem_update'),  # noqa
    url(r'^stock/item/(?P<pk>[\d]+)/delete/$', views.stockitem_delete, name='stockitem_delete'),  # noqa
    url(r'^stock/item/new/$', views.stockitem_create, name='stockitem_create'),
    url(r'^stock/item/(?P<item_pk>[\d]+)/new-specimen/$', views.specimen_create, name='specimen_create'),  # noqa
    url(r'^stock/specimen/(?P<pk>[\d]+)/edit/$', views.specimen_update, name='specimen_update'),  # noqa
    url(r'^stock/specimen/(?P<pk>[\d]+)/delete/$', views.specimen_delete, name='specimen_delete'),  # noqa
    url(r'^stock/inventory/specimen/add/(?P<inventory_pk>[\d]+)/(?P<specimen_pk>[\d]+)/$', views.inventoryspecimen_add, name='inventoryspecimen_add'),  # noqa
    url(r'^stock/inventory/specimen/increase/(?P<pk>[\d]+)/$', views.inventoryspecimen_increase, name='inventoryspecimen_increase'),  # noqa
    url(r'^stock/inventory/specimen/decrease/(?P<pk>[\d]+)/$', views.inventoryspecimen_decrease, name='inventoryspecimen_decrease'),  # noqa
    url(r'^stock/inventory/specimen/remove/(?P<inventory_pk>[\d]+)/(?P<specimen_pk>[\d]+)/$', views.inventoryspecimen_remove, name='inventoryspecimen_remove'),  # noqa
    url(r'^stock/inventory/specimen/by-barcode/$', views.inventoryspecimen_bybarcode, name='inventoryspecimen_bybarcode'),  # noqa
    url(r'^loan/$', views.loan, name='loan'),
]
