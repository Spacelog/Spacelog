from django.conf.urls.defaults import *
from django.conf import settings
#from search.views import SearchView

urlpatterns = patterns('',
    url(r'^$', 'homepage.views.homepage', name="homepage"),
    url(r'^about/$', 'homepage.views.about', name="about"),
    url(r'^press/$', 'homepage.views.press', name="press"),
    url(r'^get-involved/$', 'homepage.views.get_involved', name="get_involved"),
    # url(r'^search/$', SearchView.as_view(), name="search"),
)

if settings.DEBUG: # pragma: no cover
    urlpatterns += patterns('',
        (r'^' + settings.MISSIONS_STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MISSIONS_STATIC_ROOT
        }),
        (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT
        }),
        # (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
        #     'document_root': settings.MEDIA_ROOT
        # }),
    )

