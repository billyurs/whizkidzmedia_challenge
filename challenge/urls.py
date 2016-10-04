from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from challenge.views import FilmSearchAPI
from challenge.views import index

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^filmSearchAPI/get_values_for_auto_suggest', FilmSearchAPI.as_view()),
                       url(r'^', index, name='index'),
    # url(r'^challenge/', include('challenge.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
#if 'challenge' in settings.INSTALLED_APPS:
 #   urlpatterns += patterns('', url(r'^challenge', include('challenge.urls')))
