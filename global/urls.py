from django.urls import path
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from search.views import SearchView
from homepage import views as homepage_views

urlpatterns = [
    path('', homepage_views.homepage, name="homepage"),
    path('about/', homepage_views.about, name="about"),
    path('press/', homepage_views.press, name="press"),
    path('get-involved/', homepage_views.get_involved, name="get_involved"),
    # url(r'^search/$', SearchView.as_view(), name="search"),
]

urlpatterns += staticfiles_urlpatterns()
