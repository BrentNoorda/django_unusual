from django.conf.urls import patterns, include, url
import django_unusual.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url(r'^(.*\.mako)$', django_unusual.views.show_mako_page),
    url(r'^$', django_unusual.views.show_mako_page, {'filename':'home.mako'}),

    url(r'^(.*\.md)$', django_unusual.views.show_markdown_page),

    # Examples:
    # url(r'^$', 'django_unusual.views.home', name='home'),
    # url(r'^django_unusual/', include('django_unusual.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
