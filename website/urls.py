from django.conf.urls.defaults import *
from django.conf import settings
from transcripts.views import PageView

urlpatterns = patterns('',
    # Example:
    # (r'^website/', include('website.foo.urls')),
    
    (r'^$', 'homepage.views.homepage'),
    url(r'^view/(?:(?P<timestamp>-?[0-9]+)/)?$', PageView.as_view(), name="view_timestamp"),
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

