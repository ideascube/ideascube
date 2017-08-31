from django.conf.urls import url

from . import views


app_name = 'server'
urlpatterns = [
    url(r'^settings/$', views.server_info, name='settings'),
    url(r'^power/$', views.power, name='power'),
    url(r'^backup/$', views.backup, name='backup'),
    url(r'^battery/$', views.battery, name='battery'),
    url(r'^wifi/(?P<ssid>.+)?$', views.wifi, name='wifi'),
    url(r'^wifi_history/$', views.wifi_history, name='wifi_history'),
    url(r'^home_page/$', views.home_page, name='home_page'),
    url(r'^languages/$', views.languages, name='languages'),
]
