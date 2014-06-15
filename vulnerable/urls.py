from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from .views import UploadView

urlpatterns = patterns('',
    url(r'^$', 'vulnerable.views.CVE_2014_0472', name='home'),
    url(r'^boom/$', 'vulnerable.views.CVE_2014_0473', name='login'),
    # CVE_2014_0472
    url(r'^upload/$', UploadView.as_view(), name='upload'),
    # CVE-2014-3730
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^xss/$', 'vulnerable.views.xss', name='xss'),
)
