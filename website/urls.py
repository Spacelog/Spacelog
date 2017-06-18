from django.conf.urls import url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from glossary.views import GlossaryView
from homepage.views import HomepageView, AboutView, HomepageQuoteView
from people.views import PeopleView
from search.views import SearchView
from transcripts import views as transcripts_views
from transcripts.views import PageView, PhasesView, RangeView, ErrorView, OriginalView

tspatt = r'-?\d+:\d+:\d+:\d+'

urlpatterns = [
    url(r'^$', HomepageView.as_view(), name="homepage"),
    url(r'^homepage-quote/$', HomepageQuoteView.as_view()),
    url(r'^about/$', AboutView.as_view(), name="about"),
    url(r'^page/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    url(r'^page/(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    url(r'^(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    url(r'^stream/(?P<start>' + tspatt + ')/?$', transcripts_views.stream, name="stream"),
    url(r'^(?P<start>' + tspatt + ')/(?P<end>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    url(r'^phases/$', PhasesView.as_view(), name="phases"),
    url(r'^phases/(?P<phase_number>\d+)/$', PhasesView.as_view(), name="phases"),
    url(r'^search/$', SearchView.as_view(), name="search"),
    url(r'^people/$', PeopleView.as_view(), name="people"),
    url(r'^people/(?P<role>[-_\w]+)/$', PeopleView.as_view(), name="people"),
    url(r'^glossary/$', GlossaryView.as_view(), name="glossary"),
    url(r'^original/(?:(?P<transcript>[-_\w]+)/)?(?P<page>-?\d+)/$', OriginalView.as_view(), name="original"),
]

urlpatterns += staticfiles_urlpatterns()
