from django.urls import path, re_path
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
    path('', HomepageView.as_view(), name="homepage"),
    path('homepage-quote/', HomepageQuoteView.as_view()),
    path('about/', AboutView.as_view(), name="about"),
    re_path(r'^page/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    re_path(r'^page/(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', PageView.as_view(), name="view_page"),
    re_path(r'^(?P<start>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    re_path(r'^stream/(?P<start>' + tspatt + ')/?$', transcripts_views.stream, name="stream"),
    re_path(r'^(?P<start>' + tspatt + ')/(?P<end>' + tspatt + ')/(?:(?P<transcript>[-_\w]+)/)?$', RangeView.as_view(), name="view_range"),
    path('phases/', PhasesView.as_view(), name="phases"),
    path('phases/<int:phase_number>/', PhasesView.as_view(), name="phases"),
    path('search/', SearchView.as_view(), name="search"),
    path('people/', PeopleView.as_view(), name="people"),
    re_path(r'^people/(?P<role>[-_\w]+)/$', PeopleView.as_view(), name="people"),
    path('glossary/', GlossaryView.as_view(), name="glossary"),
    re_path(r'^original/(?:(?P<transcript>[-_\w]+)/)?(?P<page>-?\d+)/$', OriginalView.as_view(), name="original"),
]

urlpatterns += staticfiles_urlpatterns()
