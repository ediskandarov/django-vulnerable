from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'vulnerable.views.CVE_2014_0472', name='home'),
    url(r'^boom/$', 'vulnerable.views.CVE_2014_0473', name='login'),
)
