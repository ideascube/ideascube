from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.i18n import JavaScriptCatalog


from . import views

urlpatterns = i18n_patterns(
    url(r'^blog/', include('ideascube.blog.urls')),
    url(r'^library/', include('ideascube.library.urls')),
    url(r'^search/', include('ideascube.search.urls')),
    url(r'^mediacenter/', include('ideascube.mediacenter.urls')),
    url(r'^monitoring/', include('ideascube.monitoring.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^welcome_staff/$', views.welcome_staff, name='welcome_staff'),
    url(r'^server/', include('ideascube.serveradmin.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, kwargs={"next_page": "/"},
        name='logout'),
    url(r'^user/$', views.user_list, name='user_list'),
    url(r'^user/(?P<pk>[\d]+)/$', views.user_detail, name='user_detail'),
    url(r'^user/(?P<pk>[\d]+)/edit/$', views.user_update, name='user_update'),
    url(r'^user/(?P<pk>[\d]+)/set-password/$', views.set_password,
        name='user_set_password'),
    url(r'^user/new/$', views.user_create, name='user_create'),
    url(r'^user/export/$', views.user_export, name='user_export'),
    url(r'^user/import/$', views.user_import, name='user_import'),
    url(r'^user/(?P<pk>[\d]+)/delete/$',
        views.user_delete, name='user_delete'),
    url(r'^user/(?P<pk>[\d]+)/toggle-staff/$',
        views.user_toggle_staff, name='user_toggle_staff'),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(packages=['ideascube']), name='jsi18n'),
)
urlpatterns = urlpatterns + [
    url(r'^i18n/', include('django.conf.urls.i18n')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
