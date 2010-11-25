from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    # (r'^website/', include('website.foo.urls')),
    
    (r'^$', 'homepage.views.homepage'),
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

