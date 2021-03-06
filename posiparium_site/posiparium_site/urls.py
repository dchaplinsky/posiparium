from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap

from core import views as core_views
from core.sitemaps import sitemaps


urlpatterns = [
    url(r'^$', core_views.home, name='home'),
    url(r'^home_stats$', core_views.home_stats, name='home_stats'),
    url(r'^search/suggest$', core_views.SuggestView.as_view(), name="search>suggest"),
    url(r'^search$', core_views.search, name='search'),
    url(r'^mp/(?P<mp_id>\d+)$', core_views.mp, name='mp_details'),
    url(r'^minion/(?P<minion_id>\d+)$', core_views.minion, name='minion_details'),
    url(r'^(?P<county_slug>\w+)$', core_views.county, name='county'),
    url(r'^(?P<county_slug>\w+)/(?P<convocation_id>\d+)$', core_views.convocation, name='convocation'),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),

    url(r'^admin/', admin.site.urls),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
