from django.conf.urls import patterns, url
from django.conf import settings
from transcripts.views import PageView, PhasesView, RangeView, ErrorView, OriginalView
from homepage.views import HomepageView, HomepageQuoteView
from search.views import SearchView
from homepage.views import HomepageView, AboutView

tspatt = r'-?\d+:\d+:\d+:\d+'

urlpatterns = patterns('',
    url(r'^$', HomepageView.as_view(), name="homepage"),
    url(r'^homepage-quote/$', HomepageQuoteView.as_view()),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^page/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    url(r'^page/(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    url(r'^(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    url(r'^stream/(?P<start>' + tspatt + ')/?$', 'transcripts.views.stream', name="stream"),
    url(r'^(?P<start>' + tspatt + ')/(?P<end>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    url(r'^phases/$', PhasesView.as_view(), name="phases"),
    url(r'^phases/(?P<phase_number>\d+)/$', PhasesView.as_view(), name="phases"),
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^people/$', 'people.views.people', name="people"),
    url(r'^people/(?P<role>[-_\w]+)/$', 'people.views.people', name="people"),
    url(r'^glossary/$', 'glossary.views.glossary', name="glossary"),   
    url(r'^original/(?:(?P<transcript>[-_\w]+)/)?(?P<page>-?\d+)/$', OriginalView.as_view(), name="original"),
)

if settings.DEBUG: # pragma: no cover
    urlpatterns += patterns('',
        (r'^' + settings.MISSIONS_STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MISSIONS_STATIC_ROOT
        }),
        (r'^' + settings.MISSIONS_IMAGE_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MISSIONS_IMAGE_ROOT
        }),
        (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT
        }),
        # (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'django.views.static.serve', {
        #     'document_root': settings.MEDIA_ROOT
        # }),
        (r'^404/$', ErrorView.as_view()),
        (r'^500/$', ErrorView.as_view(error_code=500)),
    )

handler404 = ErrorView.as_view()
handler500 = ErrorView.as_view(error_code=500)

