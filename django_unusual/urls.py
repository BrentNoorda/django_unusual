from django.conf.urls import patterns, include, url
import django_unusual.views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# used for delivering media files from gunicorn - see gunicorn note below
import os
import django
admin_media_path = os.path.join(django.__path__[0], 'contrib', 'admin', 'static', 'admin')

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

    # when running under gunicorn, the above stops working, but still want to deliver media files, so
    # borrow a little from http://stackoverflow.com/questions/6984672/django-admin-site-not-formatted
    # and a little from https://docs.djangoproject.com/en/dev/howto/static-files/ to get this
    url(r'^static/admin/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': admin_media_path,
    }),
)
