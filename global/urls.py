from django.conf.urls import url
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from search.views import SearchView
from homepage import views as homepage_views

urlpatterns = [
    url(r'^$', homepage_views.homepage, name="homepage"),
    url(r'^about/$', homepage_views.about, name="about"),
    url(r'^press/$', homepage_views.press, name="press"),
    url(r'^get-involved/$', homepage_views.get_involved, name="get_involved"),
    # url(r'^search/$', SearchView.as_view(), name="search"),
]

urlpatterns += staticfiles_urlpatterns()
