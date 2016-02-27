from django.conf.urls import url, patterns
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from search.views import SearchView

urlpatterns = patterns('',
    url(r'^$', 'homepage.views.homepage', name="homepage"),
    url(r'^about/$', 'homepage.views.about', name="about"),
    url(r'^press/$', 'homepage.views.press', name="press"),
    url(r'^get-involved/$', 'homepage.views.get_involved', name="get_involved"),
    # url(r'^search/$', SearchView.as_view(), name="search"),
)

urlpatterns += staticfiles_urlpatterns()
