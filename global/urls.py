from django.conf.urls.defaults import *
from django.conf import settings
from search.views import SearchView

urlpatterns = patterns('',
    url(r'^$', 'homepage.views.homepage', name="homepage"),
    # url(r'^search/$', SearchView.as_view(), name="search"),
)

if settings.DEBUG: # pragma: no cover
    urlpatterns += patterns('',
        (r'^' + settings.P_STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.P_STATIC_ROOT
        }),
        # (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
        #     'document_root': settings.MEDIA_ROOT
        # }),
    )

